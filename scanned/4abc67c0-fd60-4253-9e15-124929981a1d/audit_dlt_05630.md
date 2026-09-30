# [?] node/app/event: fix data race on eventBus.prevQueueSize (#21551)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-03
Source: https://github.com/erigontech/erigon/commit/e7f75c9a700fbcd60b1d1394ec9e109c0cf5cc43
Type: security-commit

## Details
node/app/event: fix data race on eventBus.prevQueueSize (#21551)

## Summary

`eventBus.prevQueueSize` gates a debug-logging heuristic (the "Execpool
overflowing / recovering" messages), but it was read
(`eventbus.go:185`/`192`) and written (`eventbus.go:201`) without
synchronization while multiple async `Publish` goroutines run
concurrently. The race detector flags this. It's harmless to correctness
(logging only), but a genuine data race — fixed by making the field an
`atomic.Int64`.

## Context

Surfaced while investigating the disabled `node/app/component` test
package (whose `TestMain` does `os.Exit(0)`, so none of its tests run).
Re-enabling that package under `-race` flagged this race first. It's
split out here as a focused, independently-reviewable fix.

The remaining problems that keep the component package disabled —
cross-test event-subscription leakage and ~400 leaked actor goroutines
that deadlock the suite — are **not** addressed here and are tracked in
#21552.

## Testing

- `go build ./node/app/...` — clean
- `node/app/event` passes `go test -race -count=5`
- `make lint` — clean

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### node/app/event/eventbus.go
```diff
@@ -68,7 +68,7 @@ type eventBus struct {
 	handlerMap    atomic.Pointer[handlerMap]
 	writerLock    sync.Mutex // serializes Subscribe/Unsubscribe writers
 	wg            sync.WaitGroup
-	prevQueueSize int
+	prevQueueSize atomic.Int64
 }
 
 type handlerMap struct {
@@ -182,14 +182,16 @@ func (hmap *handlerMap) publish(bus *eventBus, args []interface{}, argIndex int)
 					queueSize := bus.execPool.QueueSize()
 
 					if queueSize > 0 {
-						if queueSize > bus.prevQueueSize {
+						prev := bus.prevQueueSize.Load()
+
+						if int64(queueSize) > prev {
 							if queueSize == 10 || queueSize == 20 || queueSize == 50 || queueSize%100 == 0 {
 								log.Debug("Execpool overflowing",
 									"bus", app.LogInstance(bus),
 									"poolSize", bus.execPool.PoolSize(),
 									"queueSize", bus.execPool.QueueSize())
 							}
-						} else if queueSize < bus.prevQueueSize {
+						} else if int64(queueSize) < prev {
 							if queueSize == 10 || queueSize == 20 || queueSize == 50 || queueSize%100 == 0 {
 								log.Debug("Execpool overflow recovering",
 									"bus", app.LogInstance(bus),
@@ -198,7 +200,7 @@ func (hmap *handlerMap) publish(bus *eventBus, args []interface{}, argIndex int)
 							}
 						}
 
-						bus.prevQueueSize = queueSize
+						bus.prevQueueSize.Store(int64(queueSize))
 					}
 				}
 			}
@@ -281,8 +283,7 @@ func (handler *eventHandler) doPublish(bus *eventBus, logEnabled bool, args ...i
 // NewEventBus returns new eventBus with empty handlers.
 func NewEventBus(execPool util.ExecPool) EventBus {
 	b := &eventBus{
-		execPool:      execPool,
-		prevQueueSize: 0,
+		execPool: execPool,
 	}
 	b.handlerMap.Store(&handlerMap{nil, map[reflect.Type]*handlerMap{}, []*eventHandler{}})
 	return b
```
