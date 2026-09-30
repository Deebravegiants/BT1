# [?] Fix race condition in TestWorkerPool (#482)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2023-05-16
Source: https://github.com/scroll-tech/scroll/commit/02d0ff22198e33dd2d67a546c3e76b3969317848
Type: security-commit

## Details
Fix race condition in TestWorkerPool (#482)

Co-authored-by: Péter Garamvölgyi <peter@scroll.io>

## Patch
### common/utils/workerpool/workerpool_test.go
```diff
@@ -22,14 +22,35 @@ func TestWorkerPool(t *testing.T) {
 		atomic.AddInt32(&cnt, -1)
 	}
 
-	go vwp.AddTask(task)
-	go vwp.AddTask(task)
-	go vwp.AddTask(task)
+	vwp.AddTask(task)
+	vwp.AddTask(task)
 
 	time.Sleep(600 * time.Millisecond)
 	as.Equal(int32(1), atomic.LoadInt32(&cnt))
+	vwp.AddTask(task)
 	vwp.Stop()
 	as.Equal(int32(0), atomic.LoadInt32(&cnt))
+}
+
+func TestWorkerPoolMaxWorkers(t *testing.T) {
+	as := assert.New(t)
+
+	vwp := workerpool.NewWorkerPool(2)
+	vwp.Run()
+	var cnt int32 = 3
+
+	task := func() {
+		time.Sleep(500 * time.Millisecond)
+		atomic.AddInt32(&cnt, -1)
+	}
+
+	time1 := time.Now()
+	vwp.AddTask(task)
+	vwp.AddTask(task)
+	vwp.AddTask(task)
+	vwp.Stop()
+	time2 := time.Now()
+	as.Greater(time2.Sub(time1), time.Second*1)
 
 }
 
```
