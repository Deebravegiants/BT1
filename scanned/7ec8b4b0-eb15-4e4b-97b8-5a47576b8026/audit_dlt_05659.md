# [?] Fix authentication bypass for direct `/v2/validator/*` endpoints (#16226)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-01-16
Source: https://github.com/OffchainLabs/prysm/commit/ce72deb3c04ee468f53a97e0b866c38fc44e62d3
Type: security-commit

## Details
Fix authentication bypass for direct `/v2/validator/*` endpoints (#16226)

This PR fixes a security vulnerability where authenticated endpoints
could be accessed without authorization by using direct
`/v2/validator/*` paths instead of `/api/v2/validator/*`.

The `AuthTokenHandler` middleware only checked for authentication on
requests containing `/api/v2/validator/` or `/eth/v1` prefixes, but the
same handlers are also registered for direct `/v2/validator/*` routes.
This allowed attackers to bypass authentication by simply removing the
`/api` prefix from the URL.

---------

Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

## Patch
### changelog/fix-validator-web-auth-bypass.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Prevent authentication bypass on direct `/v2/validator/*` endpoints by enforcing auth checks for non-public routes.
```

### validator/rpc/intercepter.go
```diff
@@ -37,8 +37,16 @@ func (s *Server) AuthTokenInterceptor() grpc.UnaryServerInterceptor {
 // AuthTokenHandler is an HTTP handler to authorize a route.
 func (s *Server) AuthTokenHandler(next http.Handler) http.Handler {
 	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
-		// if it's not initialize or has a web prefix
-		if (strings.Contains(r.URL.Path, api.WebApiUrlPrefix) || strings.Contains(r.URL.Path, api.KeymanagerApiPrefix)) && !strings.Contains(r.URL.Path, api.SystemLogsPrefix) {
+		path := r.URL.Path
+		needsAuth := strings.Contains(path, api.WebApiUrlPrefix) || strings.Contains(path, api.KeymanagerApiPrefix)
+		// Protect direct (non-/api) web endpoints too; otherwise callers can bypass auth by hitting /v2/validator/*.
+		if strings.HasPrefix(path, api.WebUrlPrefix) &&
+			!strings.HasPrefix(path, api.WebUrlPrefix+"initialize") &&
+			!strings.HasPrefix(path, api.WebUrlPrefix+"health/") {
+			needsAuth = true
+		}
+
+		if needsAuth && !strings.Contains(path, api.SystemLogsPrefix) {
 			// ignore some routes
 			reqToken := r.Header.Get("Authorization")
 			if reqToken == "" {
```

### validator/rpc/intercepter_test.go
```diff
@@ -107,6 +107,16 @@ func TestServer_AuthTokenHandler(t *testing.T) {
 		require.NoError(t, json.Unmarshal(rr.Body.Bytes(), errJson))
 		require.StringContains(t, "Unauthorized", errJson.Message)
 	})
+	t.Run("direct /v2 endpoint also needs auth token (no /api bypass)", func(t *testing.T) {
+		rr := httptest.NewRecorder()
+		req, err := http.NewRequest(http.MethodGet, "/v2/validator/beacon/status", http.NoBody)
+		require.NoError(t, err)
+		testHandler.ServeHTTP(rr, req)
+		require.Equal(t, http.StatusUnauthorized, rr.Code)
+		errJson := &httputil.DefaultJsonError{}
+		require.NoError(t, json.Unmarshal(rr.Body.Bytes(), errJson))
+		require.StringContains(t, "Unauthorized", errJson.Message)
+	})
 	t.Run("initialize does not need auth", func(t *testing.T) {
 		rr := httptest.NewRecorder()
 		req, err := http.NewRequest(http.MethodGet, api.WebUrlPrefix+"initialize", http.NoBody)
```
