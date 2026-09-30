# [?] fix of panic on stop

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2020-12-18
Source: https://github.com/0xsoniclabs/sonic/commit/1a764883cad77f61bf1ddf221943329ced957b72
Type: security-commit

## Details
fix of panic on stop

fatal error: concurrent map read and map write
goroutine 409 [running]:
runtime.throw(0x1323f7e, 0x21)
        /usr/local/go/src/runtime/panic.go:1116 +0x72 fp=0xc0006ed0e8 sp=0xc0006ed0b8 pc=0x44b622
runtime.mapaccess1(0x114e020, 0xc0003dec30, 0xc0006ed220, 0x33df85389f39d200)
        /usr/local/go/src/runtime/map.go:411 +0x24b fp=0xc0006ed128 sp=0xc0006ed0e8 pc=0x424b0b
github.com/ethereum/go-ethereum/trie.(*Database).Cap(0xc0000a1520, 0x0, 0x0, 0x0)
        /home/fabel/go/pkg/mod/github.com/uprendis/go-ethereum@v1.9.22-ftm-0.2/trie/database.go:598 +0x278 fp=0xc0006ed420 sp=0xc0006ed128 pc=0x793d98
github.com/Fantom-foundation/go-opera/gossip/evmstore.(*Store).Commit(0xc000252240, 0x7f85f2a5be98, 0x0)
        /home/fabel/Work/fantom/go-opera/gossip/evmstore/store.go:81 +0x4f fp=0xc0006ed478 sp=0xc0006ed420 pc=0xd14edf
github.com/Fantom-foundation/go-opera/gossip.(*Store).Commit(0xc000103980, 0xc0006ed648, 0x20, 0x20, 0xc00297be01, 0xc0003c24b0, 0x2, 0x2)
        /home/fabel/Work/fantom/go-opera/gossip/store.go:155 +0xa2 fp=0xc0006ed4f0 sp=0xc0006ed478 pc=0xd851e2
github.com/Fantom-foundation/go-opera/gossip.(*Service).processEvent(0xc0001b1800, 0xc002a5c120, 0x0, 0x0)
        /home/fabel/Work/fantom/go-opera/gossip/c_event_callbacks.go:136 +0x696 fp=0xc0006ed730 sp=0xc0006ed4f0 pc=0xd6a286
github.com/Fantom-foundation/go-opera/gossip.(*Service).processEvent-fm(0xc002a5c120, 0x16cd7c02a0b6, 0x22da0a0)
        /home/fabel/Work/fantom/go-opera/gossip/c_event_callbacks.go:63 +0x34 fp=0xc0006ed760 sp=0xc0006ed730 pc=0xd94ae4
github.com/Fantom-foundation/go-opera/gossip.(*ProtocolManager).makeProcessor.func4(0x1588fe0, 0xc002a5c120, 0x0, 0x0)
        /home/fabel/Work/fantom/go-opera/gossip/handler.go:272 +0x128 fp=0xc0006ed950 sp=0xc0006ed760 pc=0xd90a58
github.com/Fantom-foundation/lachesis-base/gossip/dagordering.(*EventsBuffer).processCompleteEvent(0xc0006d4370, 0xc0025f69c0, 0xc0003fed00, 0x2, 0x2, 0xc9f7c5)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/gossip/dagordering/event_buffer.go:143 +0x51 fp=0xc0006ed998 sp=0xc0006ed950 pc=0xd40951
github.com/Fantom-foundation/lachesis-base/gossip/dagordering.(*EventsBuffer).pushEvent(0xc0006d4370, 0xc0025f69c0, 0x230aa50, 0x0, 0x0, 0x0, 0xc00279ed68)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/gossip/dagordering/event_buffer.go:90 +0xe2 fp=0xc0006edad8 sp=0xc0006ed998 pc=0xd400a2
github.com/Fantom-foundation/lachesis-base/gossip/dagordering.(*EventsBuffer).PushEvent(0xc0006d4370, 0x1588fe0, 0xc002a5c120, 0xc000130810, 0x10, 0x0)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/gossip/dagordering/event_buffer.go:68 +0x201 fp=0xc0006edb68 sp=0xc0006edad8 pc=0xd3fef1
github.com/Fantom-foundation/lachesis-base/gossip/dagprocessor.(*Processor).process(0xc00046b9a0, 0xc000130810, 0x10, 0x1588fe0, 0xc002a5c120, 0x0, 0x0, 0x230aa50, 0x0, 0x0)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/gossip/dagprocessor/processor.go:176 +0x6c fp=0xc0006edba8 sp=0xc0006edb68 pc=0xd41ecc
github.com/Fantom-foundation/lachesis-base/gossip/dagprocessor.(*Processor).Enqueue.func1()
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/gossip/dagprocessor/processor.go:154 +0x594 fp=0xc0006edf08 sp=0xc0006edba8 pc=0xd42894
github.com/Fantom-foundation/lachesis-base/utils/workers.worker(0xc00033fbc0, 0xc0001b22a0)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/utils/workers/workers.go:66 +0x3b fp=0xc0006edfa0 sp=0xc0006edf08 pc=0xd168db
github.com/Fantom-foundation/lachesis-base/utils/workers.(*Workers).Start.func1(0xc0001d2f60)
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/utils/workers/workers.go:31 +0x5e fp=0xc0006edfd8 sp=0xc0006edfa0 pc=0xd169ee
runtime.goexit()
        /usr/local/go/src/runtime/asm_amd64.s:1373 +0x1 fp=0xc0006edfe0 sp=0xc0006edfd8 pc=0x47e7b1
created by github.com/Fantom-foundation/lachesis-base/utils/workers.(*Workers).Start
        /home/fabel/go/pkg/mod/github.com/rus-alex/lachesis-base@v0.0.0-20201214165924-72afa56d8136/utils/workers/workers.go:29 +0x63

## Patch
### gossip/service.go
```diff
@@ -344,6 +344,7 @@ func (s *Service) Stop() error {
 	defer s.engineMu.Unlock()
 	s.stopped = true
 
+	s.blockProcWg.Wait()
 	return s.store.Commit()
 }
 
```
