# [?] Protect exported participant methods with tryLock on a mutex, panicking if it fails. (#329)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2024-06-10
Source: https://github.com/filecoin-project/go-f3/commit/462de82c9a15254bc8d1fe36c335bb30fe0b9e39
Type: security-commit

## Details
Protect exported participant methods with tryLock on a mutex, panicking if it fails. (#329)

## Patch
### gpbft/api.go
```diff
@@ -25,28 +25,29 @@ type ValidatedMessage interface {
 }
 
 // Receives a Granite protocol message.
+// Calls to methods on this interface are expected to be serialized.
+// The methods are not safe for concurrent use, and may panic if called concurrently.
 type MessageReceiver interface {
 	// Receives a validated Granite message from some other participant.
 	// Returns an error, wrapping (use errors.Is()/Unwrap()):
 	// - ErrValidationTooOld if the message is for a prior instance
 	// - ErrValidationWrongBase if the message has an invalid base chain
 	// - ErrReceivedAfterTermination if the message is received after the instance has terminated (a programming error)
 	// - both ErrReceivedInternalError and a cause if there was an internal error processing the message
-	// This method is not safe for concurrent use.
 	ReceiveMessage(msg ValidatedMessage) error
 	// ReceiveAlarm signals the trigger of the alarm set by Clock.SetAlarm. Note that
 	// triggering alarms takes precedence over ReceiveMessage, i.e. when an alarm is
 	// triggered at the same time as an arrival of a message ReceiveAlarm must be
 	// called before ReceiveMessage.
-	//
-	// This method is not safe for concurrent use.
 	ReceiveAlarm() error
 }
 
-// Interface which network participants must implement.
+// Interface from host to a network participant.
+// Calls to methods on this interface are expected to be serialized.
+// The methods are not safe for concurrent use, and may panic if called concurrently.
 type Receiver interface {
 	// Begins executing the protocol.
-	// The node will request the canonical chain to propose from the host.
+	// The node will subsequently request the canonical chain to propose from the host.
 	Start() error
 	// SkipToInstance jumps directly to a given instance.
 	// This can be triggered by the reception of a valid finality certificate, or
```

### gpbft/participant.go
```diff
@@ -14,11 +14,15 @@ type Participant struct {
 	*options
 	host Host
 
+	// Mutex for detecting concurrent invocation of stateful API methods.
+	// To be taken at the top of public API methods, and always taken before instanceMutex,
+	// if both are to be taken.
+	apiMutex sync.Mutex
 	// Mutex protecting currentInstance and committees cache for concurrent validation.
 	// Note that not every access need be protected:
 	// - writes to currentInstance, and reads from it during validation,
 	// - reads from or writes to committees (which is written during validation).
-	mutex sync.Mutex
+	instanceMutex sync.Mutex
 	// Instance identifier for the current (or, if none, next to start) GPBFT instance.
 	currentInstance uint64
 	// Cache of committees for the current or future instances.
@@ -69,34 +73,47 @@ func NewParticipant(host Host, o ...Option) (*Participant, error) {
 	}, nil
 }
 
-// Start uses SkipToInstance under the hood to trigger
-// the start of the first instance.
-// This way we handle in an homogeneous way the start of
-// new instances
 func (p *Participant) Start() (err error) {
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
 	defer func() {
 		if r := recover(); r != nil {
 			err = &PanicError{Err: r}
 		}
 	}()
-	return p.SkipToInstance(p.currentInstance)
+	// Uses skipToInstance to trigger the start of the first instance,
+	// so all instances are started the same way.
+	p.doSkipToInstance(p.currentInstance)
+	return nil
 }
 
 func (p *Participant) CurrentRound() uint64 {
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
 	if p.gpbft == nil {
 		return 0
 	}
 	return p.gpbft.round
 }
 
 func (p *Participant) CurrentInstance() uint64 {
-	p.mutex.Lock()
-	defer p.mutex.Unlock()
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
+	p.instanceMutex.Lock()
+	defer p.instanceMutex.Unlock()
 	return p.currentInstance
 }
 
 // Validates a message
 func (p *Participant) ValidateMessage(msg *GMessage) (valid ValidatedMessage, err error) {
+	// This method is not protected by the API mutex, it is intended for concurrent use.
+	// The instance mutex is taken when appropriate by inner methods.
 	defer func() {
 		if r := recover(); r != nil {
 			err = &PanicError{Err: r}
@@ -117,6 +134,10 @@ func (p *Participant) ValidateMessage(msg *GMessage) (valid ValidatedMessage, er
 
 // Receives a validated Granite message from some other participant.
 func (p *Participant) ReceiveMessage(vmsg ValidatedMessage) (err error) {
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
 	defer func() {
 		if r := recover(); r != nil {
 			err = &PanicError{Err: r}
@@ -144,6 +165,10 @@ func (p *Participant) ReceiveMessage(vmsg ValidatedMessage) (err error) {
 }
 
 func (p *Participant) ReceiveAlarm() (err error) {
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
 	defer func() {
 		if r := recover(); r != nil {
 			err = &PanicError{Err: r}
@@ -163,12 +188,21 @@ func (p *Participant) ReceiveAlarm() (err error) {
 
 // Triggers the start to the instance defined as an argument.
 func (p *Participant) SkipToInstance(i uint64) (err error) {
+	if !p.apiMutex.TryLock() {
+		panic("concurrent API method invocation")
+	}
+	defer p.apiMutex.Unlock()
 	defer func() {
 		if r := recover(); r != nil {
 			err = &PanicError{Err: r}
 		}
 	}()
 
+	p.doSkipToInstance(i)
+	return nil
+}
+
+func (p *Participant) doSkipToInstance(i uint64) {
 	// Finish current instance to clean old committees and old messages queued
 	// and prepare to begin a new instance.
 	p.finishCurrentInstance(i)
@@ -177,8 +211,6 @@ func (p *Participant) SkipToInstance(i uint64) (err error) {
 	// This will fetch the chain, drain existing messages for that instance,
 	// and start the instance.
 	p.host.SetAlarm(p.host.Time())
-
-	return err
 }
 
 func (p *Participant) beginInstance() error {
@@ -221,8 +253,8 @@ func (p *Participant) beginInstance() error {
 
 // Fetches the committee against which to validate messages for some instance.
 func (p *Participant) fetchCommittee(instance uint64) (*committee, error) {
-	p.mutex.Lock()
-	defer p.mutex.Unlock()
+	p.instanceMutex.Lock()
+	defer p.instanceMutex.Unlock()
 
 	// Reject messages for past instances.
 	if instance < p.currentInstance {
@@ -261,8 +293,8 @@ func (p *Participant) finishCurrentInstance(nextInstance uint64) {
 	}
 	p.gpbft = nil
 
-	p.mutex.Lock()
-	defer p.mutex.Unlock()
+	p.instanceMutex.Lock()
+	defer p.instanceMutex.Unlock()
 	// clean all messages queued and old committees for instances below the next
 	// one
 	for i := p.currentInstance; i < nextInstance; i++ {
```
