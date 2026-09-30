# [?] [queue/hardening] error instead of panic when adding to stopped q (#33)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-02-08
Source: https://github.com/berachain/beacon-kit/commit/f5b5e050970059f73ea60ffcd6211e26ef802447
Type: security-commit

## Details
[queue/hardening] error instead of panic when adding to stopped q (#33)

* throw error instead of panic when adding to stopped queue

## Patch
### async/dispatch/queue/errors.go
```diff
@@ -0,0 +1,30 @@
+// SPDX-License-Identifier: MIT
+//
+// Copyright (c) 2023 Berachain Foundation
+//
+// Permission is hereby granted, free of charge, to any person
+// obtaining a copy of this software and associated documentation
+// files (the "Software"), to deal in the Software without
+// restriction, including without limitation the rights to use,
+// copy, modify, merge, publish, distribute, sublicense, and/or sell
+// copies of the Software, and to permit persons to whom the
+// Software is furnished to do so, subject to the following
+// conditions:
+//
+// The above copyright notice and this permission notice shall be
+// included in all copies or substantial portions of the Software.
+//
+// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
+// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
+// OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
+// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
+// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
+// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
+// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
+// OTHER DEALINGS IN THE SOFTWARE.
+
+package queue
+
+import "errors"
+
+var ErrAddToStoppedQueue = errors.New("cannot add to stopped queue")
```

### async/dispatch/queue/queue.go
```diff
@@ -69,38 +69,45 @@ func NewDispatchQueue(
 }
 
 // Async adds a work item to the queue to be executed asynchronously.
-func (q *DispatchQueue) Async(execute WorkItem) {
+func (q *DispatchQueue) Async(execute WorkItem) error {
 	q.mu.Lock()
 	defer q.mu.Unlock()
 
 	if q.stopped {
-		panic("Queue has been stopped")
+		return ErrAddToStoppedQueue
 	}
 
 	q.wg.Add(1)
 	q.queue <- execute
+	return nil
 }
 
 // AsyncAfter adds a work item to the queue to be executed after a specified duration.
-func (q *DispatchQueue) AsyncAfter(deadline time.Duration, execute WorkItem) {
+func (q *DispatchQueue) AsyncAfter(deadline time.Duration, execute WorkItem) error {
 	time.Sleep(deadline)
-	q.Async(execute)
+	return q.Async(execute)
 }
 
 // Sync adds a work item to the queue and waits for its execution to complete.
-func (q *DispatchQueue) Sync(execute WorkItem) {
+func (q *DispatchQueue) Sync(execute WorkItem) error {
 	done := make(chan struct{})
-	q.Async(func() {
+	if err := q.Async(func() {
 		execute()
 		close(done)
-	})
+	}); err != nil {
+		return err
+	}
 	<-done
+	return nil
 }
 
 // AsyncAndWait adds a work item to the queue and waits for all work items to complete.
-func (q *DispatchQueue) AsyncAndWait(execute WorkItem) {
-	q.Async(execute)
+func (q *DispatchQueue) AsyncAndWait(execute WorkItem) error {
+	if err := q.Async(execute); err != nil {
+		return err
+	}
 	q.wg.Wait()
+	return nil
 }
 
 // Stop stops the queue, preventing new work items from being added and waits for all
```

### async/dispatch/queue/queue_test.go
```diff
@@ -32,6 +32,7 @@ import (
 	"time"
 
 	"github.com/itsdevbear/bolaris/async/dispatch/queue"
+	"github.com/stretchr/testify/assert"
 )
 
 func TestDispatchQueueConcurrent_Async(t *testing.T) {
@@ -45,10 +46,12 @@ func TestDispatchQueueConcurrent_Async(t *testing.T) {
 	wg.Add(10)
 
 	for i := 0; i < 10; i++ {
-		q.Async(func() {
+		if err := q.Async(func() {
 			defer wg.Done()
 			counter.Add(1)
-		})
+		}); err != nil {
+			t.Errorf("unexpected error: %v", err)
+		}
 	}
 
 	wg.Wait()
@@ -70,10 +73,13 @@ func TestDispatchQueueConcurrent_AsyncAfter(t *testing.T) {
 
 	startTime := time.Now()
 	waitTime := time.Millisecond * 100
-	q.AsyncAfter(waitTime, func() {
+	err := q.AsyncAfter(waitTime, func() {
 		asyncAfterExecuted = true
 		wg.Done()
 	})
+	if err != nil {
+		t.Errorf("unexpected error: %v", err)
+	}
 
 	wg.Wait()
 
@@ -93,9 +99,12 @@ func TestDispatchQueueConcurrent_Sync(t *testing.T) {
 
 	var syncExecuted bool
 
-	q.Sync(func() {
+	err := q.Sync(func() {
 		syncExecuted = true
 	})
+	if err != nil {
+		t.Errorf("unexpected error: %v", err)
+	}
 
 	if !syncExecuted {
 		t.Errorf("Sync function did not execute")
@@ -109,9 +118,12 @@ func TestDispatchQueueConcurrent_AsyncAndWait(t *testing.T) {
 
 	var asyncAndWaitExecuted bool
 
-	q.AsyncAndWait(func() {
+	err := q.AsyncAndWait(func() {
 		asyncAndWaitExecuted = true
 	})
+	if err != nil {
+		t.Errorf("unexpected error: %v", err)
+	}
 
 	if !asyncAndWaitExecuted {
 		t.Errorf("AsyncAndWait function did not execute")
@@ -125,22 +137,23 @@ func TestDispatchQueueConcurrent_Stop(t *testing.T) {
 
 	// Add some items to the queue
 	for i := 0; i < 10; i++ {
-		q.Async(func() {
+		if err := q.Async(func() {
 			time.Sleep(time.Millisecond * 100)
-		})
+		}); err != nil {
+			t.Errorf("unexpected error: %v", err)
+		}
 	}
 
 	// Stop the queue
 	q.Stop()
 
 	// Try to add another item to the queue, it should panic
 	defer func() {
-		if r := recover(); r == nil {
-			t.Errorf("Expected panic after Stop, but none occurred")
-		}
 	}()
 
-	q.Async(func() {
+	if err := q.Async(func() {
 		t.Errorf("Async function executed after Stop")
-	})
+	}); err == nil {
+		assert.Equal(t, err, queue.ErrAddToStoppedQueue)
+	}
 }
```

### async/dispatch/queue/single.go
```diff
@@ -41,7 +41,7 @@ func NewSingleDispatchQueue() *SingleDispatchQueue {
 }
 
 // Async adds a work item to the queue to be executed asynchronously.
-func (q *SingleDispatchQueue) Async(item WorkItem) {
+func (q *SingleDispatchQueue) Async(item WorkItem) error {
 	q.mu.Lock()
 	defer q.mu.Unlock()
 
@@ -59,4 +59,5 @@ func (q *SingleDispatchQueue) Async(item WorkItem) {
 	// Push the new item.
 	q.wg.Add(1)
 	q.queue <- item
+	return nil
 }
```

### async/dispatch/queue/single_test.go
```diff
@@ -48,7 +48,7 @@ func TestSingleDispatchQueueReplace(t *testing.T) {
 	// We will only execute two tasks in total.
 	allWorkDone.Add(2)
 
-	q.Async(func() {
+	if err := q.Async(func() {
 		defer allWorkDone.Done()
 		mu.Lock()
 		defer mu.Unlock()
@@ -59,32 +59,38 @@ func TestSingleDispatchQueueReplace(t *testing.T) {
 		// Block on the condition variable to simulate a long-running task.
 		cond.Wait()
 		output = append(output, 1)
-	})
+	}); err != nil {
+		t.Errorf("Unexpected err %v", err)
+	}
 
 	// Wait for the first async function to start
 	// before enqueueing the next two.
 	firstWorkStarted.Wait()
 
 	// These tasks should get replaced over and over by each other.
 	for i := 2; i < 69; i++ {
-		q.Async(func() {
+		if err := q.Async(func() {
 			defer allWorkDone.Done()
 
 			mu.Lock()
 			defer mu.Unlock()
 			output = append(output, i)
-		})
+		}); err != nil {
+			t.Errorf("Unexpected err %v", err)
+		}
 	}
 
 	// Since the first Async called hasn't exited yet (it's waiting on the condition variable),
 	// the last Async should be enqueued and all others should've been replaced.
-	q.Async(func() {
+	if err := q.Async(func() {
 		defer allWorkDone.Done()
 
 		mu.Lock()
 		defer mu.Unlock()
 		output = append(output, 69)
-	})
+	}); err != nil {
+		t.Errorf("Unexpected err %v", err)
+	}
 
 	// Signal the condition variable to wake up the first async function.
 	cond.Signal()
```

### async/dispatch/types.go
```diff
@@ -34,11 +34,12 @@ import (
 // Queue represents a queue of work items to be executed. It's interface is inspired by
 // Apple's Grand Central Dispatch (GCD) API.
 // https://developer.apple.com/documentation/dispatch/dispatchqueue
+// TODO: use error groups
 type Queue interface {
-	Async(queue.WorkItem)
-	AsyncAfter(time.Duration, queue.WorkItem)
-	Sync(queue.WorkItem)
-	AsyncAndWait(queue.WorkItem)
+	Async(queue.WorkItem) error
+	AsyncAfter(time.Duration, queue.WorkItem) error
+	Sync(queue.WorkItem) error
+	AsyncAndWait(queue.WorkItem) error
 }
 
 // Event represents actions that occur during consensus. Listeners can
```

### async/notify/service.go
```diff
@@ -91,9 +91,13 @@ func (s *Service) Start() {
 					select {
 					case event := <-ch:
 						// Use the dispatch queue to call the handler's Handle method asynchronously
-						s.gcd.GetQueue(pair.queueID).Async(func() {
+						if err := s.gcd.GetQueue(pair.queueID).Async(func() {
 							pair.handler.HandleNotification(event)
-						})
+						}); err != nil {
+							// Choosing to panic here because it doesn't make sense for the
+							// service we're controlling to have stopped the queue
+							panic(err)
+						}
 					case <-subscription.Err():
 						return
 					case <-s.stop:
```

### beacon/execution/service.go
```diff
@@ -90,9 +90,11 @@ func (s *Service) NotifyForkchoiceUpdate(
 	var err error
 
 	// Push the forkchoice request to the forkchoice dispatcher, we want to block until
-	s.GCD().GetQueue(forkchoiceDispatchQueue).Sync(func() {
+	if e := s.GCD().GetQueue(forkchoiceDispatchQueue).Sync(func() {
 		err = s.notifyForkchoiceUpdate(ctx, fcuConfig)
-	})
+	}); e != nil {
+		return e
+	}
 
 	return err
 }
```
