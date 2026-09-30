# [?] Fix PanicError construction and sim clock progress with historical messages. (#120)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2024-03-14
Source: https://github.com/filecoin-project/go-f3/commit/0e2629ce1517a6339b1ad285f62687dfa9628248
Type: security-commit

## Details
Fix PanicError construction and sim clock progress with historical messages. (#120)

Co-authored-by: Jakub Sztandera <kubuxu@protonmail.ch>

## Patch
### gpbft/participant.go
```diff
@@ -25,17 +25,13 @@ type Participant struct {
 }
 
 type PanicError struct {
-	Err error
+	Err any
 }
 
 func (e *PanicError) Error() string {
 	return fmt.Sprintf("panic recovered: %v", e.Err)
 }
 
-func (e *PanicError) Unwrap() error {
-	return e.Err
-}
-
 func NewParticipant(id ActorID, config GraniteConfig, host Host) *Participant {
 	return &Participant{id: id, config: config, host: host}
 }
@@ -67,7 +63,7 @@ func (p *Participant) CurrentRound() uint64 {
 func (p *Participant) ReceiveECChain(chain ECChain) (err error) {
 	defer func() {
 		if r := recover(); r != nil {
-			err = &PanicError{Err: err}
+			err = &PanicError{Err: r}
 		}
 	}()
 
@@ -84,7 +80,7 @@ func (p *Participant) ReceiveECChain(chain ECChain) (err error) {
 func (p *Participant) ValidateMessage(msg *GMessage) (checked bool, err error) {
 	defer func() {
 		if r := recover(); r != nil {
-			err = &PanicError{Err: err}
+			err = &PanicError{Err: r}
 		}
 	}()
 
@@ -106,7 +102,7 @@ func (p *Participant) ValidateMessage(msg *GMessage) (checked bool, err error) {
 func (p *Participant) ReceiveMessage(msg *GMessage) (accepted bool, err error) {
 	defer func() {
 		if r := recover(); r != nil {
-			err = &PanicError{Err: err}
+			err = &PanicError{Err: r}
 		}
 	}()
 
@@ -126,7 +122,7 @@ func (p *Participant) ReceiveMessage(msg *GMessage) (accepted bool, err error) {
 func (p *Participant) ReceiveAlarm() (err error) {
 	defer func() {
 		if r := recover(); r != nil {
-			err = &PanicError{Err: err}
+			err = &PanicError{Err: r}
 		}
 	}()
 
```

### sim/network.go
```diff
@@ -162,7 +162,9 @@ func (n *Network) Tick(adv AdversaryReceiver) (bool, error) {
 	}
 
 	msg := n.queue.Remove(i)
-	n.clock = msg.deliverAt
+	if msg.deliverAt.After(n.clock) {
+		n.clock = msg.deliverAt
+	}
 	payloadStr, ok := msg.payload.(string)
 	receiver := n.participants[msg.dest]
 	if ok && strings.HasPrefix(payloadStr, "ALARM") {
```

### test/honest_test.go
```diff
@@ -141,7 +141,7 @@ func TestSyncHalvesBLS(t *testing.T) {
 
 func TestAsyncHalves(t *testing.T) {
 	t.Parallel()
-	for n := 4; n <= 2; n += 2 {
+	for n := 4; n <= 20; n += 2 {
 		for i := 0; i < ASYNC_ITERS; i++ {
 			sm := sim.NewSimulation(newAsyncConfig(n, i), GraniteConfig(), sim.TraceNone)
 			a := sm.Base(0).Extend(sm.CIDGen.Sample())
```
