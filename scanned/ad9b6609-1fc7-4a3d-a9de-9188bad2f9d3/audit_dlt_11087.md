# [?] [conductor] Fix test race condition (#13314)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-12-08
Source: https://github.com/bobanetwork/boba/commit/2824b3b2c001f07c582c37213e6f0152b12ac3e2
Type: security-commit

## Details
[conductor] Fix test race condition (#13314)

* Fix conductor test race condition

* update

* Address shell ci check

* rerun CI for non-related issue

## Patch
### op-conductor/conductor/service.go
```diff
@@ -381,9 +381,7 @@ func (oc *OpConductor) Start(ctx context.Context) error {
 	oc.log.Info("OpConductor started")
 	// queue an action in case sequencer is not in the desired state.
 	oc.prevState = NewState(oc.leader.Load(), oc.healthy.Load(), oc.seqActive.Load())
-	// Immediately queue an action. This is made blocking to ensure that start is not
-	// considered complete until the first action is executed.
-	oc.actionCh <- struct{}{}
+	oc.queueAction()
 
 	return nil
 }
```

### op-conductor/conductor/service_test.go
```diff
@@ -106,7 +106,7 @@ func (s *OpConductorTestSuite) SetupSuite() {
 	s.metrics = &metrics.NoopMetricsImpl{}
 	s.cfg = mockConfig(s.T())
 	s.version = "v0.0.1"
-	s.next = make(chan struct{}, 1)
+	s.next = make(chan struct{})
 }
 
 func (s *OpConductorTestSuite) SetupTest() {
@@ -129,7 +129,8 @@ func (s *OpConductorTestSuite) SetupTest() {
 	s.conductor.leaderUpdateCh = s.leaderUpdateCh
 
 	s.err = errors.New("error")
-	s.syncEnabled = false // default to no sync, turn it on by calling s.enableSynchronization()
+	s.syncEnabled = false   // default to no sync, turn it on by calling s.enableSynchronization()
+	s.wg = sync.WaitGroup{} // create new wg for every test in case last test didn't finish the action loop during shutdown.
 }
 
 func (s *OpConductorTestSuite) TearDownTest() {
@@ -876,6 +877,5 @@ func (s *OpConductorTestSuite) TestHandleInitError() {
 }
 
 func TestControlLoop(t *testing.T) {
-	t.Skipf("Skipping test, it's flaky and needs to be fixed")
 	suite.Run(t, new(OpConductorTestSuite))
 }
```

### op-conductor/run_test_1000times.sh
```diff
@@ -2,10 +2,11 @@
 
 set -e
 
-for i in {1..100}; do
+for i in {1..1000}; do
   echo "======================="
   echo "Running iteration $i"
-  if ! gotestsum -- -run 'TestControlLoop' ./... --count=1 --timeout=5s -race; then
+
+  if ! go test -v ./conductor/... -race -count=1; then
     echo "Test failed"
     exit 1
   fi
```
