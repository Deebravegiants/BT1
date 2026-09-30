# [?] Merge pull request #21 from libp2p/bug/panic-after-close

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-08-06
Source: https://github.com/libp2p/go-libp2p/commit/b64949277434d5aac10dd9475440c8e081228f41
Type: security-commit

## Details
Merge pull request #21 from libp2p/bug/panic-after-close

[DEPENDENT MERGE] Return error rather than panic in Emit

## Patch
### p2p/host/eventbus/basic.go
```diff
@@ -28,16 +28,17 @@ type emitter struct {
 	dropper func(reflect.Type)
 }
 
-func (e *emitter) Emit(evt interface{}) {
+func (e *emitter) Emit(evt interface{}) error {
 	if atomic.LoadInt32(&e.closed) != 0 {
-		panic("emitter is closed")
+		return fmt.Errorf("emitter is closed")
 	}
 	e.n.emit(evt)
+	return nil
 }
 
 func (e *emitter) Close() error {
 	if !atomic.CompareAndSwapInt32(&e.closed, 0, 1) {
-		panic("closed an emitter more than once")
+		return fmt.Errorf("closed an emitter more than once")
 	}
 	if atomic.AddInt32(&e.n.nEmitters, -1) == 0 {
 		e.dropper(e.typ)
```

### p2p/host/eventbus/basic_test.go
```diff
@@ -109,18 +109,13 @@ func TestEmitOnClosed(t *testing.T) {
 		t.Fatal(err)
 	}
 	em.Close()
-
-	defer func() {
-		r := recover()
-		if r == nil {
-			t.Errorf("expected panic")
-		}
-		if r.(string) != "emitter is closed" {
-			t.Error("unexpected message")
-		}
-	}()
-
-	em.Emit(EventA{})
+	err = em.Emit(EventA{})
+	if err == nil {
+		t.Errorf("expected error")
+	}
+	if err.Error() != "emitter is closed" {
+		t.Error("unexpected message")
+	}
 }
 
 func TestClosingRaces(t *testing.T) {
```
