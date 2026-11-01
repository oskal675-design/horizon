# #5977: Horizon server tick-step verification

Server fix: `58a3d74122e8b3000c90c257e8eeeb77e55604e2` over main `e6eed3e11`.

The pre-fix server binary was built at `003985afa4d80d0728600d162a769d08fcc2c00e`; its clock.rs is byte-for-byte identical to the base. The before/after screenshots run the actual Minecraft 26.3 graphical client (SDL offscreen), not the headless codec observer.

`before.png` and `after.png` show the second frozen extension step. The pre-fix client never receives a nonzero single-step allowance and leaves piston progress at zero. The fixed server sends the requested allowance before its piston event; the real client advances the block entity. `vanilla-reference.png` is a separate run against a real vanilla server.

The graphical runs cover 16 snapshots: east/up sticky-piston extension/retraction and power changes while frozen. 48/48 block states and moving-BE presence match the vanilla reference. Float progress is recorded for diagnosis, **not asserted equal across independent graphical runs**: the arrival of step/event packets relative to a client's frame affects this phase. Snapshot waits verify unchanged server game time. `PistonGraphicalClient.java` and `probe-piston-graphical.py` are the original diagnostic drivers; run them from a prepared Horizon checkout, with the Java observer compiled into `.local/piston-graphical`.

`baseline-network.txt` shows the actual off-by-one notification counts. `fixed-network.txt` and `native-network.txt` record the committed permanent harness's exact packet contract: requested counts, cancellation, remaining zero on a late join, and step notification before piston events for both observers. The headless observer uses native codecs and does not render a client.

`combined-results.json`: **18/18 pass** with the server fix and #6042's client gate applied together. The guard was applied only to clean remote.rs after saving the server commit, built in the existing target, and restored afterward. Two real Horizon processes (dedicated server and graphical client) cover east/up extension/retraction, frozen power changes, and unfreeze controls. Each frozen snapshot waits 20 client ticks, checks unchanged authoritative game time and checks the authoritative block with execute-if before reading the client. Live moving-BE NBT is not exposed by Horizon's data-get path, so no saved-progress assertion was made in this combined run. The expected block lifecycle is established independently by the real vanilla run in #6042.

No game JARs, assets, prepared resources, or Mojang source are included. The drivers are original test code; the images are test screenshots.
