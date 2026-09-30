# [?] Handle panics correctly in logging util (#551)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-02-08
Source: https://github.com/sei-protocol/sei-chain/commit/caaddba7b02cf510b4776cee679d7f4fd41eec33
Type: security-commit

## Details
Handle panics correctly in logging util (#551)

* Handle panics correctly in logging util

* better testing

## Patch
### utils/logging/time.go
```diff
@@ -10,7 +10,13 @@ import (
 func LogIfNotDoneAfter[R any](logger log.Logger, task func() (R, error), after time.Duration, label string) (R, error) {
 	resultChan := make(chan R, 1)
 	errChan := make(chan error, 1)
+	panicChan := make(chan any, 1)
 	go func() {
+		defer func() {
+			if err := recover(); err != nil {
+				panicChan <- err
+			}
+		}()
 		res, err := task()
 		if err != nil {
 			errChan <- err
@@ -25,6 +31,9 @@ func LogIfNotDoneAfter[R any](logger log.Logger, task func() (R, error), after t
 		case err := <-errChan:
 			var res R
 			return res, err
+		case err := <-panicChan:
+			// reraise panic in main goroutine
+			panic(err)
 		case <-time.After(after):
 			logger.Error(fmt.Sprintf("%s still not finished after %s", label, after))
 		}
```

### utils/logging/time_test.go
```diff
@@ -70,3 +70,20 @@ func TestSlowError(t *testing.T) {
 	require.Empty(t, res)
 	require.Equal(t, fmt.Sprintf("test still not finished after %s", after), logger.lastError)
 }
+
+func TestPanic(t *testing.T) {
+	logger := mockLogger{}
+	task := func() (bool, error) {
+		panic("test")
+	}
+	after := 1 * time.Second
+	outer := func() {
+		defer func() {
+			if err := recover(); err != nil {
+			}
+		}()
+		LogIfNotDoneAfter(&logger, task, after, "test")
+	}
+	require.Panics(t, func() { LogIfNotDoneAfter(&logger, task, after, "test") })
+	require.NotPanics(t, outer)
+}
```
