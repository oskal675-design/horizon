import sys,os,time,subprocess,argparse,json,threading,tempfile
from pathlib import Path
root=Path.cwd();sys.path.insert(0,str(root/'tools'))
import vanilla_client as v
from integration_env import game_environment
from test_locator_bar_parity import server_dir
from test_dedicated_server_parity import Server,game_time
ap=argparse.ArgumentParser();ap.add_argument('--server',default='vanilla');ap.add_argument('--binary');args=ap.parse_args()
build=root/'.local/piston-graphical'/args.server;build.mkdir(parents=True,exist_ok=True)
world=root/'.local/piston-step-server-parity/generate/world'
port=server_dir(build/'server',world)
server_cmd=([root/'.local/toolchains/java/bin/java','-Xmx2g','-jar',root/'.local/downloads/server-26.3.jar','nogui'] if args.server.startswith('vanilla') else [args.binary or root/'launcher/target/fast/horizon-client','--resources',root/'.local/horizon-client/26.3','--dedicated','--nogui'])
server=Server(server_cmd,build/'server',args.server)
client=None
lines=[]
def wait(pattern,timeout=120):
 deadline=time.monotonic()+timeout
 while not any(pattern in x for x in lines):
  if client.poll() is not None:raise RuntimeError('client exited: '+''.join(lines[-15:]))
  if time.monotonic()>deadline:raise TimeoutError(pattern+' '+''.join(lines[-10:]))
  time.sleep(.1)
def snapshot(label):
 before=game_time(server);client.stdin.write(label+'\n');client.stdin.flush();wait('Saved screenshot as '+label+'.png',30);time.sleep(.3);assert game_time(server)==before, ('frozen time advanced',label)
try:
 server.wait_for(r'Done \(')
 game=build/'client';game.mkdir(exist_ok=True)
 v.write_options(game,{'enableVsync':'false','renderDistance':'2','guiScale':'2'})
 opt=argparse.Namespace(game_dir=game,assets=root/'.local/minecraft-install/assets',heap='2G',name='Alice',width=960,height=720,join=f'127.0.0.1:{port}',world=None,lan_port=None,backend='opengl')
 cmd=v.command(opt);idx=cmd.index('-cp')+1;cmd[idx]=str(root/'.local/piston-graphical')+os.pathsep+cmd[idx];cmd[cmd.index('net.minecraft.client.main.Main')]='dev.horizonlab.parity.PistonGraphicalClient'
 scratch=tempfile.mkdtemp(prefix='piston-native-');env=game_environment(v.environment(),scratch);env.update(SDL_VIDEODRIVER='offscreen',LIBGL_ALWAYS_SOFTWARE='1')
 client=subprocess.Popen(list(map(str,cmd)),cwd=game,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 log=(build/'client.log').open('w')
 def pump():
  for line in client.stdout:lines.append(line);log.write(line);log.flush()
 threading.Thread(target=pump,daemon=True).start()
 server.wait_for('Alice joined the game',timeout=150);time.sleep(5)
 for c in ['gamerule spawn_mobs false','time set day','weather clear','fill -6 79 -6 8 79 6 stone','fill -6 80 -6 8 85 6 air','setblock 4 80 -4 stone','tp Alice 4.5 81 -3.5 40 20','tick freeze']:
  server.console(c)
 game_time(server);time.sleep(1)
 for direction,stone,power in [('east','1 80 0','-1 80 0'),('up','0 81 0','0 79 0')]:
  server.console('fill -3 79 -2 3 84 2 air');game_time(server);time.sleep(.4)
  for c in [f'setblock 0 80 0 sticky_piston[facing={direction}]',f'setblock {stone} stone',f'setblock {power} redstone_block']:server.console(c)
  game_time(server);time.sleep(.5);snapshot(direction+'-powered')
  for action in ['extend','retract']:
   if action=='retract':
    server.console(f'setblock {power} air');game_time(server);time.sleep(.4);snapshot(direction+'-unpowered')
   for step in range(1,4):
    before=game_time(server);server.console('tick step 1')
    deadline=time.monotonic()+20
    while game_time(server)==before:
     if time.monotonic()>deadline:raise TimeoutError('step')
    time.sleep(1);snapshot(direction+'-'+action+'-'+str(step))
 (build/'client-states.txt').write_text(''.join(x for x in lines if 'PISTON' in x))
 print(''.join(x for x in lines if 'PISTON' in x))
finally:
 if client:
  client.terminate()
  try:client.wait(timeout=15)
  except subprocess.TimeoutExpired:client.kill();client.wait()
 server.stop()
