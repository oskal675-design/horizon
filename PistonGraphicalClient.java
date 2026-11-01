package dev.horizonlab.parity;
import java.io.*;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.piston.PistonMovingBlockEntity;
public final class PistonGraphicalClient {
 public static void main(String[] args) throws Exception {
  Thread watcher=new Thread(()->{
   try(var input=new BufferedReader(new InputStreamReader(System.in))) {
    for(String line;(line=input.readLine())!=null;) {
     final String command=line;
     Minecraft mc;
     while((mc=Minecraft.getInstance())==null) Thread.sleep(100);
     final Minecraft game=mc;
     game.execute(()->{
      try {
       if(command.equals("quit")){game.stop();return;}
       if(game.level==null||game.player==null){System.out.println("PISTON no-level");return;}
       var hidden=net.minecraft.client.gui.Hud.class.getDeclaredField("isHidden");hidden.setAccessible(true);hidden.setBoolean(game.gui.hud,true);
       for(int x=0;x<=2;x++) {
        BlockPos pos=command.startsWith("up-")?new BlockPos(0,80+x,0):new BlockPos(x,80,0);var be=game.level.getBlockEntity(pos);
        System.out.println("PISTON "+command+" "+x+" "+game.level.getBlockState(pos)+" entity="+(be==null?"null":be.getClass().getSimpleName())+(be instanceof PistonMovingBlockEntity piston?" progress="+piston.getProgress(0)+" current="+piston.getProgress(1):""));
       }
       net.minecraft.client.Screenshot.grab(game.gameDirectory,command+".png",game.gameRenderer.mainRenderTarget(),1, m->System.out.println("PISTON screenshot "+m.getString()));
       System.out.flush();
      }catch(Throwable error){error.printStackTrace();}
     });
    }
   } catch(Throwable error){error.printStackTrace();}
  },"piston-observer");watcher.setDaemon(true);watcher.start();
  net.minecraft.client.main.Main.main(args);
 }
}
