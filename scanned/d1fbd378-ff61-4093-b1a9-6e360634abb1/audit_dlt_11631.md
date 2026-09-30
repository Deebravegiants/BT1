# [?] fix(claimsmanager): check index to avoid runtime panic (#1223)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2024-03-05
Source: https://github.com/quicksilver-zone/quicksilver/commit/9aaad177e14048f32767b23dab020d3f6f82b3a9
Type: security-commit

## Details
fix(claimsmanager): check index to avoid runtime panic (#1223)

## Patch
### x/claimsmanager/keeper/grpc_query.go
```diff
@@ -71,7 +71,7 @@ func (k Keeper) UserClaims(c context.Context, q *types.QueryClaimsRequest) (*typ
 		// check for the presence of the addr bytes in the key.
 		// first prefix byte is 0x00; so cater for that! Then + 1 to skip the separator.
 		idx := bytes.Index(key[1:], []byte{0x00}) + 1 + 1
-		if bytes.Equal(key[idx:idx+len(addrBytes)], addrBytes) {
+		if idx >= 0 && bytes.Equal(key[idx:idx+len(addrBytes)], addrBytes) {
 			out = append(out, claim)
 		}
 		return false
@@ -88,7 +88,7 @@ func (k Keeper) UserLastEpochClaims(c context.Context, q *types.QueryClaimsReque
 		// check for the presence of the addr bytes in the key.
 		// First byte is 0x01 here, so no need to consider it; + 1 to skip the separator.
 		idx := bytes.Index(key, []byte{0x00}) + 1
-		if bytes.Equal(key[idx:idx+len(addrBytes)], addrBytes) {
+		if idx >= 0 && bytes.Equal(key[idx:idx+len(addrBytes)], addrBytes) {
 			out = append(out, claim)
 		}
 		return false
```
