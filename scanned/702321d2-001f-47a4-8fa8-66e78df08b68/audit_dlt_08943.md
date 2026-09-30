# [?] fix(vald): bus panics when block channel closes (#685)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-07-30
Source: https://github.com/axelarnetwork/axelar-core/commit/08db681c1639dbf66489844461cc1e1b52917f6e
Type: security-commit

## Details
fix(vald): bus panics when block channel closes (#685)

## Patch
### cmd/axelard/cmd/vald/events/bus.go
```diff
@@ -114,10 +114,15 @@ func (m *EventBus) FetchEvents(ctx context.Context) <-chan error {
 
 		for {
 			select {
-			case block := <-blockResults:
+			case block, ok := <-blockResults:
+				if !ok {
+					m.shutdown()
+					continue
+				}
 				if err := m.publishEvents(block); err != nil {
 					errChan <- err
-					return
+					m.shutdown()
+					continue
 				}
 			case <-m.running.Done():
 				m.logger.Info("closing all subscriptions")
```

### cmd/axelard/cmd/vald/events/bus_test.go
```diff
@@ -21,7 +21,7 @@ import (
 
 func TestMgr_FetchEvents(t *testing.T) {
 
-	t.Run("returns error", func(t *testing.T) {
+	t.Run("WHEN the event source throws an error THEN the bus returns error", func(t *testing.T) {
 		bus := func() pubsub.Bus { return &mock.BusMock{} }
 		errors := make(chan error, 1)
 		source := &mock.BlockSourceMock{
@@ -38,6 +38,36 @@ func TestMgr_FetchEvents(t *testing.T) {
 		err := <-errChan
 		assert.Error(t, err)
 	})
+
+	t.Run("WHEN the block source block result channel closes THEN the bus shuts down", func(t *testing.T) {
+		busMock := &mock.BusMock{
+			SubscribeFunc: func() (pubsub.Subscriber, error) {
+				return &mock.SubscriberMock{}, nil
+			},
+			CloseFunc: func() {},
+		}
+		busFactory := func() pubsub.Bus { return busMock }
+		results := make(chan *coretypes.ResultBlockResults)
+		source := &mock.BlockSourceMock{
+			BlockResultsFunc: func(ctx context.Context) (<-chan *coretypes.ResultBlockResults, <-chan error) {
+				return results, nil
+			},
+		}
+		mgr := events.NewEventBus(source, busFactory, log.TestingLogger())
+
+		mgr.FetchEvents(context.Background())
+
+		close(results)
+
+		timeout, cancel := context.WithTimeout(context.Background(), 1*time.Second)
+		defer cancel()
+		select {
+		case <-mgr.Done():
+			return
+		case <-timeout.Done():
+			assert.FailNow(t, "timed out")
+		}
+	})
 }
 
 func TestMgr_Subscribe(t *testing.T) {
```
