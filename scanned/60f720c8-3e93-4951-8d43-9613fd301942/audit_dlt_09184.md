# [?] fix panic in TestSubFailFully (#48)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-08-17
Source: https://github.com/libp2p/go-libp2p/commit/e5728a280376f6f8d8efac511ecc4a1b39762f1f
Type: security-commit

## Details
fix panic in TestSubFailFully (#48)

## Patch
### p2p/host/eventbus/basic_test.go
```diff
@@ -455,11 +455,6 @@ func TestCloseBlocking(t *testing.T) {
 	sub.Close() // cancel sub
 }
 
-func panicOnTimeout(d time.Duration) {
-	<-time.After(d)
-	panic("timeout reached")
-}
-
 func TestSubFailFully(t *testing.T) {
 	bus := NewBus()
 	em, err := bus.Emitter(new(EventB))
@@ -472,9 +467,17 @@ func TestSubFailFully(t *testing.T) {
 		t.Fatal(err)
 	}
 
-	go panicOnTimeout(5 * time.Second)
+	done := make(chan struct{})
+	go func() {
+		defer close(done)
+		em.Emit(EventB(159)) // will hang if sub doesn't fail properly
+	}()
 
-	em.Emit(EventB(159)) // will hang if sub doesn't fail properly
+	select {
+	case <-done:
+	case <-time.After(5 * time.Second):
+		t.Fatal("timeout")
+	}
 }
 
 func testMany(t testing.TB, subs, emits, msgs int, stateful bool) {
```
