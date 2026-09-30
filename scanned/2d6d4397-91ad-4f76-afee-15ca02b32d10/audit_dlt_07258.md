# [?] privval: increase timeout to mitigate non-deterministic test failure (#3580)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-04-22
Source: https://github.com/cometbft/cometbft/commit/8db7e74b873712b4bb3c72616a798d3fb82094e9
Type: security-commit

## Details
privval: increase timeout to mitigate non-deterministic test failure (#3580)

This should fix #3576 (ran it many times locally but only time will tell). The test actually only checked for the opcode of the error. From the name of the test we actually want to test if we see a timeout after a pre-defined time.

## Commits:

* increase readWrite timeout as it is also used in the `Accept` of the tcp
listener:

 - before this caused the readWriteTimeout to kick in (rarely) while Accept
 - as a side-effect: remove obsolete time.Sleep: in both listener cases
 the Accept will only return after successfully accepting and the timeout
 that is supposed to be tested here will be triggered because there is a
 read without a write
 - see if we actually run into a timeout error (the whole purpose of
 this test AFAIU)

Signed-off-by: Ismail Khoffi <Ismail.Khoffi@gmail.com>

* makee local test-vars `const`

Signed-off-by: Ismail Khoffi <Ismail.Khoffi@gmail.com>

## Additional comments:

@xla: Confusing how an accept could take longer than that, but assuming a noisy environment full of little docker whales will be slower than what 50 years of silicon are capable of. The only thing I'd be vary of is that we mask structural issues with the code by just bumping the timeout, if we are sensitive towards that it warrants invesigation, but again this might only be true in the environment our CI runs in.

## Patch
### privval/socket_listeners_test.go
```diff
@@ -97,7 +97,15 @@ func TestListenerTimeoutAccept(t *testing.T) {
 }
 
 func TestListenerTimeoutReadWrite(t *testing.T) {
-	for _, tc := range listenerTestCases(t, time.Second, time.Millisecond) {
+	const (
+		// This needs to be long enough s.t. the Accept will definitely succeed:
+		timeoutAccept = time.Second
+		// This can be really short but in the TCP case, the accept can
+		// also trigger a timeoutReadWrite. Hence, we need to give it some time.
+		// Note: this controls how long this test actually runs.
+		timeoutReadWrite = 10 * time.Millisecond
+	)
+	for _, tc := range listenerTestCases(t, timeoutAccept, timeoutReadWrite) {
 		go func(dialer SocketDialer) {
 			_, err := dialer()
 			if err != nil {
@@ -110,8 +118,7 @@ func TestListenerTimeoutReadWrite(t *testing.T) {
 			t.Fatal(err)
 		}
 
-		time.Sleep(2 * time.Millisecond)
-
+		// this will timeout because we don't write anything:
 		msg := make([]byte, 200)
 		_, err = c.Read(msg)
 		opErr, ok := err.(*net.OpError)
@@ -122,5 +129,9 @@ func TestListenerTimeoutReadWrite(t *testing.T) {
 		if have, want := opErr.Op, "read"; have != want {
 			t.Errorf("for %s listener, have %v, want %v", tc.description, have, want)
 		}
+
+		if have, want := opErr.Timeout(), true; have != want {
+			t.Errorf("for %s listener, got unexpected error: have %v, want %v", tc.description, have, want)
+		}
 	}
 }
```
