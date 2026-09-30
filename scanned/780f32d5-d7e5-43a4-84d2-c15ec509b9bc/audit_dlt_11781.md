# [?] Bump `/x/net` dependency to resolve CVE-2024-45338 (#811)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2025-01-07
Source: https://github.com/filecoin-project/go-f3/commit/44f252ecd5dfa7d1a2cd81b2a5436eb89dec03b2
Type: security-commit

## Details
Bump `/x/net` dependency to resolve CVE-2024-45338 (#811)

Dependabot auto dependency update seems to be failing.
Hence, the manual update.

See:
 * https://github.com/filecoin-project/go-f3/security/dependabot/13
 * https://github.com/filecoin-project/go-f3/actions/runs/12649345441/job/35245556074

## Patch
### go.mod
```diff
@@ -137,7 +137,7 @@ require (
 	go.uber.org/fx v1.23.0 // indirect
 	go.uber.org/mock v0.5.0 // indirect
 	golang.org/x/mod v0.21.0 // indirect
-	golang.org/x/net v0.30.0 // indirect
+	golang.org/x/net v0.33.0 // indirect
 	golang.org/x/sys v0.28.0 // indirect
 	golang.org/x/text v0.21.0 // indirect
 	golang.org/x/tools v0.26.0 // indirect
```

### go.sum
```diff
@@ -524,8 +524,8 @@ golang.org/x/net v0.9.0/go.mod h1:d48xBJpPfHeWQsugry2m+kC02ZBRGRgulfHnEXEuWns=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/net v0.14.0/go.mod h1:PpSgVXXLK0OxS0F31C1/tv6XNguvCrnXIDrFMspZIUI=
 golang.org/x/net v0.20.0/go.mod h1:z8BVo6PvndSri0LbOE3hAn0apkU+1YvI6E70E9jsnvY=
-golang.org/x/net v0.30.0 h1:AcW1SDZMkb8IpzCdQUaIq2sP4sZ4zw+55h6ynffypl4=
-golang.org/x/net v0.30.0/go.mod h1:2wGyMJ5iFasEhkwi13ChkO/t1ECNC4X4eBKkVFyYFlU=
+golang.org/x/net v0.33.0 h1:74SYHlV8BIgHIFC/LrYkOGIwL19eTYXQ5wc6TBuO36I=
+golang.org/x/net v0.33.0/go.mod h1:HXLR5J+9DxmrqMwG9qjGCxZ+zKXxBru04zlTvWlWuN4=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20181017192945-9dcd33a902f4/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20181203162652-d668ce993890/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
```
