# [?] fix(header/sync): fix possible out of bounds panic (#1892)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-03-10
Source: https://github.com/celestiaorg/celestia-node/commit/e3432b798b2eb22cd194a90215f7c6def15c7c1f
Type: security-commit

## Details
fix(header/sync): fix possible out of bounds panic (#1892)

Also renamed Before to Truncate.

## Patch
### libs/header/sync/ranges.go
```diff
@@ -126,11 +126,15 @@ func (r *headerRange[H]) Head() H {
 	return r.headers[ln-1]
 }
 
-// Before truncates all the headers before height 'end' - [r.Start:end]
-func (r *headerRange[H]) Before(end uint64) ([]H, uint64) {
+// Truncate truncates all the headers before height 'end' - [r.Start:end]
+func (r *headerRange[H]) Truncate(end uint64) []H {
 	r.lk.Lock()
 	defer r.lk.Unlock()
 
+	if r.start > end {
+		return nil
+	}
+
 	amnt := uint64(len(r.headers))
 	if r.start+amnt >= end {
 		amnt = end - r.start + 1 // + 1 to include 'end' as well
@@ -141,5 +145,6 @@ func (r *headerRange[H]) Before(end uint64) ([]H, uint64) {
 	if len(r.headers) != 0 {
 		r.start = uint64(r.headers[0].Height())
 	}
-	return out, amnt
+
+	return out
 }
```

### libs/header/sync/ranges_test.go
```diff
@@ -32,3 +32,15 @@ func TestAddParallel(t *testing.T) {
 		last = r.start
 	}
 }
+
+func TestRangeTruncate(t *testing.T) {
+	n := 300
+	suite := test.NewTestSuite(t)
+	headers := suite.GenDummyHeaders(n)
+
+	r := newRange(headers[200])
+	r.Append(headers[201:]...)
+
+	truncated := r.Truncate(100)
+	assert.Nil(t, truncated)
+}
```

### libs/header/sync/sync.go
```diff
@@ -262,8 +262,8 @@ func (s *Syncer[H]) processHeaders(
 			break
 		}
 
-		headers, amount := headersRange.Before(to)
-		if amount == 0 {
+		headers := headersRange.Truncate(to)
+		if len(headers) == 0 {
 			break
 		}
 
```
