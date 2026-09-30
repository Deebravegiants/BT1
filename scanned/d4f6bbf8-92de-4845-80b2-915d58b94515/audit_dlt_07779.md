# [?] moving event channel and removing close channel there to prevent potential panic (#15359)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2025-05-30
Source: https://github.com/OffchainLabs/prysm/commit/711984d9428b3c721b90ff90a7106d78c36c66fe
Type: security-commit

## Details
moving event channel and removing close channel there to prevent potential panic (#15359)

## Patch
### changelog/james-prysm_move-event-channel.md
```diff
@@ -0,0 +1,3 @@
+### Ignored
+
+- code cleanup moving event channel into the validator struct for function cleanups.
\ No newline at end of file
```

### validator/client/grpc-api/grpc_validator_client.go
```diff
@@ -257,7 +257,6 @@ func (c *grpcValidatorClient) StartEventStream(ctx context.Context, topics []str
 		select {
 		case <-ctx.Done():
 			log.Info("Context canceled, stopping event stream")
-			close(eventsChannel)
 			c.isEventStreamRunning = false
 			return
 		default:
```

### validator/client/iface/validator.go
```diff
@@ -36,6 +36,7 @@ const (
 // Validator interface defines the primary methods of a validator client.
 type Validator interface {
 	Done()
+	EventsChan() <-chan *event.Event
 	AccountsChangedChan() <-chan [][fieldparams.BLSPubkeyLength]byte
 	WaitForChainStart(ctx context.Context) error
 	WaitForSync(ctx context.Context) error
@@ -60,7 +61,7 @@ type Validator interface {
 	CheckDoppelGanger(ctx context.Context) error
 	PushProposerSettings(ctx context.Context, slot primitives.Slot, forceFullPush bool) error
 	SignValidatorRegistrationRequest(ctx context.Context, signer SigningFunc, newValidatorRegistration *ethpb.ValidatorRegistrationV1) (*ethpb.SignedValidatorRegistrationV1, bool /* isCached */, error)
-	StartEventStream(ctx context.Context, topics []string, eventsChan chan<- *event.Event)
+	StartEventStream(ctx context.Context, topics []string)
 	EventStreamIsRunning() bool
 	ProcessEvent(ctx context.Context, event *event.Event)
 	ProposerSettings() *proposer.Settings
```

### validator/client/runner.go
```diff
@@ -54,9 +54,8 @@ func run(ctx context.Context, v iface.Validator) {
 		handleAssignmentError(err, headSlot)
 	}
 	startCancel()
-	eventsChan := make(chan *event.Event, 1)
 	healthTracker := v.HealthTracker()
-	runHealthCheckRoutine(ctx, v, eventsChan)
+	runHealthCheckRoutine(ctx, v)
 
 	// check if proposer settings is still nil
 	// Set properties on the beacon node like the fee recipient for validators that are being used & active.
@@ -149,7 +148,7 @@ func run(ctx context.Context, v iface.Validator) {
 				}
 				dutiesCancel()
 			}
-		case e := <-eventsChan:
+		case e := <-v.EventsChan():
 			v.ProcessEvent(ctx, e)
 		case currentKeys := <-v.AccountsChangedChan(): // should be less of a priority than next slot
 			onAccountsChanged(ctx, v, currentKeys)
@@ -312,7 +311,7 @@ func handleAssignmentError(err error, slot primitives.Slot) {
 	}
 }
 
-func runHealthCheckRoutine(ctx context.Context, v iface.Validator, eventsChan chan<- *event.Event) {
+func runHealthCheckRoutine(ctx context.Context, v iface.Validator) {
 	log.Info("Starting health check routine for beacon node apis")
 	healthCheckTicker := time.NewTicker(time.Duration(params.BeaconConfig().SecondsPerSlot) * time.Second)
 	tracker := v.HealthTracker()
@@ -343,7 +342,7 @@ func runHealthCheckRoutine(ctx context.Context, v iface.Validator, eventsChan ch
 			// in case of node returning healthy but event stream died
 			if isHealthy && !v.EventStreamIsRunning() {
 				log.Info("Event stream reconnecting...")
-				go v.StartEventStream(ctx, event.DefaultEventTopics, eventsChan)
+				go v.StartEventStream(ctx, event.DefaultEventTopics)
 			}
 		}
 	}()
```

### validator/client/service.go
```diff
@@ -6,6 +6,7 @@ import (
 	"strings"
 	"time"
 
+	eventClient "github.com/OffchainLabs/prysm/v6/api/client/event"
 	grpcutil "github.com/OffchainLabs/prysm/v6/api/grpc"
 	"github.com/OffchainLabs/prysm/v6/async/event"
 	lruwrpr "github.com/OffchainLabs/prysm/v6/cache/lru"
@@ -223,6 +224,7 @@ func (v *ValidatorService) Start() {
 		distributed:                    v.distributed,
 		disableDutiesPolling:           v.disableDutiesPolling,
 		accountsChangedChannel:         make(chan [][fieldparams.BLSPubkeyLength]byte, 1),
+		eventsChannel:                  make(chan *eventClient.Event, 1),
 	}
 
 	v.validator = valStruct
```

### validator/client/testutil/mock_validator.go
```diff
@@ -75,6 +75,10 @@ func (fv *FakeValidator) Done() {
 	fv.DoneCalled = true
 }
 
+func (fv *FakeValidator) EventsChan() <-chan *event.Event {
+	return fv.EventsChannel
+}
+
 func (fv *FakeValidator) AccountsChangedChan() <-chan [][fieldparams.BLSPubkeyLength]byte {
 	return fv.AccountsChannel
 }
@@ -323,7 +327,7 @@ func (fv *FakeValidator) DeleteGraffiti(_ context.Context, _ [fieldparams.BLSPub
 	return nil
 }
 
-func (*FakeValidator) StartEventStream(_ context.Context, _ []string, _ chan<- *event.Event) {
+func (*FakeValidator) StartEventStream(_ context.Context, _ []string) {
 
 }
 
```

### validator/client/validator.go
```diff
@@ -114,6 +114,7 @@ type validator struct {
 	dutiesLock                         sync.RWMutex
 	disableDutiesPolling               bool
 	accountsChangedChannel             chan [][fieldparams.BLSPubkeyLength]byte
+	eventsChannel                      chan *eventClient.Event
 	accountChangedSub                  event.Subscription
 }
 
@@ -138,6 +139,10 @@ func (v *validator) Done() {
 	}
 }
 
+func (v *validator) EventsChan() <-chan *eventClient.Event {
+	return v.eventsChannel
+}
+
 func (v *validator) AccountsChangedChan() <-chan [][fieldparams.BLSPubkeyLength]byte {
 	return v.accountsChangedChannel
 }
@@ -1145,9 +1150,9 @@ func (v *validator) PushProposerSettings(ctx context.Context, slot primitives.Sl
 	return nil
 }
 
-func (v *validator) StartEventStream(ctx context.Context, topics []string, eventsChannel chan<- *eventClient.Event) {
+func (v *validator) StartEventStream(ctx context.Context, topics []string) {
 	log.WithField("topics", topics).Info("Starting event stream")
-	v.validatorClient.StartEventStream(ctx, topics, eventsChannel)
+	v.validatorClient.StartEventStream(ctx, topics, v.eventsChannel)
 }
 
 func (v *validator) checkDependentRoots(ctx context.Context, head *structs.HeadEvent) error {
```
