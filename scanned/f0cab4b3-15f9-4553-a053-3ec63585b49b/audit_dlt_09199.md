# [?] fix close deadlock and Sub type error

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-06-22
Source: https://github.com/libp2p/go-libp2p/commit/de37ea9063136aead391e3e7659402032f3abb4a
Type: security-commit

## Details
fix close deadlock and Sub type error

## Patch
### p2p/host/eventbus/basic.go
```diff
@@ -104,22 +104,38 @@ func (s *sub) Out() <-chan interface{} {
 }
 
 func (s *sub) Close() error {
-	close(s.ch)
+	stop := make(chan struct{})
+	go func() {
+		for {
+			select {
+			case <-s.ch:
+			case <-stop:
+				close(s.ch)
+				return
+			}
+		}
+	}()
+
 	for _, n := range s.nodes {
 		n.lk.Lock()
+
 		for i := 0; i < len(n.sinks); i++ {
 			if n.sinks[i] == s.ch {
 				n.sinks[i], n.sinks[len(n.sinks)-1] = n.sinks[len(n.sinks)-1], nil
 				n.sinks = n.sinks[:len(n.sinks)-1]
 				break
 			}
 		}
+
 		tryDrop := len(n.sinks) == 0 && atomic.LoadInt32(&n.nEmitters) == 0
+
 		n.lk.Unlock()
+
 		if tryDrop {
 			s.dropper(n.typ)
 		}
 	}
+	close(stop)
 	return nil
 }
 
@@ -148,12 +164,14 @@ func (b *basicBus) Subscribe(evtTypes interface{}, opts ...event.SubscriptionOpt
 		dropper: b.tryDropNode,
 	}
 
-	for i, etyp := range types {
-		typ := reflect.TypeOf(etyp)
-
-		if typ.Kind() != reflect.Ptr {
+	for _, etyp := range types {
+		if reflect.TypeOf(etyp).Kind() != reflect.Ptr {
 			return nil, errors.New("subscribe called with non-pointer type")
 		}
+	}
+
+	for i, etyp := range types {
+		typ := reflect.TypeOf(etyp)
 
 		err = b.withNode(typ.Elem(), func(n *node) {
 			n.sinks = append(n.sinks, out.ch)
```

### p2p/host/eventbus/basic_test.go
```diff
@@ -297,6 +297,27 @@ func TestStateful(t *testing.T) {
 	}
 }
 
+func TestCloseBlocking(t *testing.T) {
+	bus := NewBus()
+	em, err := bus.Emitter(new(EventB))
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	sub, err := bus.Subscribe(new(EventB))
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	go func() {
+		em.Emit(EventB(159))
+	}()
+
+	time.Sleep(10 * time.Millisecond) // make sure that emit is blocked
+
+	sub.Close() // cancel sub
+}
+
 func testMany(t testing.TB, subs, emits, msgs int, stateful bool) {
 	if race.WithRace() && subs+emits > 5000 {
 		t.SkipNow()
```
