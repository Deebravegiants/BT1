### Title
Overly Permissive Bearer Token Parsing in Gateway HTTP Server Silently Accepts Malformed Authorization Schemes - (File: core/services/gateway/network/httpserver.go)

### Summary
The chainlink gateway's user-facing HTTP server extracts the JWT/vault auth token from the `Authorization` header using `strings.TrimPrefix(authHeader, "Bearer ")` without first validating that the header actually conforms to the RFC 6750 `Bearer` scheme. [1](#0-0)  This mirrors the Keycloak bug class (CWE-551 / GHSA-gv94-wp4h-vv8p): the auth-scheme check is not performed before the token is parsed and forwarded downstream — any value in the header is accepted and passed on as the "token," regardless of case, spacing, or whether the "Bearer" scheme keyword is present at all.

### Finding Description
In `httpServer.handleRequest`, the authorization token used for the entire request lifecycle is derived like this:
```go
authHeader := r.Header.Get("Authorization")
jwtToken := ""
if authHeader != "" {
    jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
}
``` [1](#0-0) 

Go's `strings.TrimPrefix` only strips the prefix if it matches exactly; if it doesn't match (e.g., different case `"bearer "`, a tab instead of a space `"Bearer\t"`, or no scheme keyword at all such as a bare token or `Basic ...`), it silently returns the original, unmodified string. There is no rejection, no scheme validation, and no case-normalization step performed before the resulting `jwtToken` is handed to `s.handler.ProcessRequest` [2](#0-1) , which flows into `gateway.ProcessRequest` and ultimately `jsonrpc2.DecodeRequest[...](rawRequest, auth)` [3](#0-2) .

This is precisely the "authorization before parsing/canonicalization" defect: the server should first confirm the scheme token is exactly `Bearer` (case-sensitively, per RFC 6750, with proper separator validation) and reject the request if not, *before* treating any part of the header as a credential. Instead, it always optimistically treats whatever remains after a best-effort trim as the credential and forwards it into request processing, deferring all correctness checking to whatever downstream signature/JWT validation exists — with no clear boundary indicating "this request had no valid Bearer credential" versus "this request had a malformed/garbage credential that happened to fail validation."

This is also the sole authentication-relevant `Authorization` header parser for the gateway's public user-facing HTTP endpoint (as opposed to the metrics/prometheus endpoint in `core/web/router.go`, which does a strict full-string equality check [4](#0-3)  and is not vulnerable to this class of issue).

### Impact Explanation
Because the scheme is not validated before parsing, non-conformant `Authorization` headers are not uniformly rejected at the transport boundary. Any client can send arbitrary header casing/formatting (`bearer x`, `BEARER\tx`, headers with extra whitespace, or headers using an entirely different scheme keyword) and have that value blindly forwarded as the request's `auth`/JWT credential into the JSON-RPC decoding and vault/workflow request-processing pipeline [3](#0-2) . While downstream JWT signature verification is expected to reject invalid tokens, the lack of a strict, fail-closed scheme check at the parsing boundary removes a defense-in-depth layer and creates ambiguity about what counts as "no credential supplied" vs. "malformed credential" — which is exactly the kind of RFC-non-compliant leniency that has historically enabled downstream authentication bypasses when combined with permissive credential validators (as in the Keycloak advisory). The severity is bounded by the strength of whatever JWT/signature validation happens later in the pipeline, which was not part of the indexed code reachable here.

### Likelihood Explanation
This code path is on the primary internet-facing entry point of the gateway (`s.handler.ProcessRequest`, invoked from `handleRequest` for every incoming user HTTP request) [5](#0-4) , so it is trivially reachable by any unprivileged client without any special network position or prior authentication — just sending a crafted `Authorization` header value.

### Recommendation
Validate the `Authorization` header strictly before extracting a token: split on the first whitespace, require the scheme token to case-sensitively equal `Bearer` per RFC 6750, and reject (401) any request where the scheme does not match exactly, rather than silently falling back to the raw header value via `TrimPrefix`. Perform this authorization-scheme check before any downstream parsing/decoding of the credential.

### Proof of Concept
1. Send a request to the gateway's user HTTP endpoint with header `Authorization: bearer <token>` (lowercase) or `Authorization: Bearer\t<token>` (tab separator).
2. Because `strings.TrimPrefix(authHeader, "Bearer ")` only strips on an exact match, the mismatched header is returned unchanged, so `jwtToken` becomes the full string `"bearer <token>"` (or similar), not the actual RFC-conformant `<token>` value. [1](#0-0) 
3. This malformed value is passed straight to `ProcessRequest`/`jsonrpc2.DecodeRequest` [3](#0-2)  without the server ever rejecting the request for using a non-conformant scheme, demonstrating that authorization-scheme validation is absent/ordered incorrectly relative to parsing.

*Note: full confirmation of whether this leads to an exploitable authentication bypass would require inspecting the downstream JWT/signature verification logic in `chainlink-common`'s `jsonrpc2.DecodeRequest` and the vault request processor, which are not part of the indexed contents available here.*

### Citations

**File:** core/services/gateway/network/httpserver.go (L195-234)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/gateway.go (L221-226)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
```

**File:** core/web/router.go (L684-696)
```go
		header := c.Request.Header.Get("Authorization")

		if header == "" {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}

		bearer := "Bearer " + token

		if header != bearer {
			c.String(http.StatusUnauthorized, ginprom.ErrInvalidToken.Error())
			return
		}
```
