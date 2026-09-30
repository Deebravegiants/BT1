# [?] prevent overflow when begin > end

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-08-04
Source: https://github.com/0xsoniclabs/sonic/commit/6325099eda86f8918749be0bf04d1c7c0e48cdaa
Type: security-commit

## Details
prevent overflow when begin > end

## Patch
### gossip/filters/filter.go
```diff
@@ -126,6 +126,9 @@ func (f *Filter) Logs(ctx context.Context) ([]*types.Log, error) {
 	if f.end < 0 {
 		end = head
 	}
+	if begin > end {
+		return []*types.Log{}, nil
+	}
 
 	if isEmpty(f.topics) && len(f.addresses) == 0 {
 		return f.unindexedLogs(ctx, begin, end)
```
