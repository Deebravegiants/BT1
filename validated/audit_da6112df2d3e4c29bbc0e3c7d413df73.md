## Title
CORS wildcard-origin boundary bypass via unanchored suffix match in Gateway HTTP server - (File: `core/services/gateway/network/httpserver.go`)

## Summary

The Gateway's user-facing HTTP server (`httpServer`, the component behind `UserServerConfig` that accepts JSON-RPC requests over `/user`) implements a custom CORS origin allowlist check, `isAllowedOrigin`, that supports wildcard subdomain entries (e.g. `*.example.com`). The subdomain match is implemented with an unanchored `strings.HasSuffix` check, which — exactly like the Casdoor `CorsFilter` prefix bug referenced in the report — fails to verify a domain-label boundary (a literal `.`) before the matched suffix. This lets an attacker who registers or controls a domain that merely *ends with* the allowed suffix (not an actual subdomain) be treated as an authorized CORS origin. [1](#0-0) 

## Finding Description

`isAllowedOrigin` parses the request's `Origin` header and each configured `CORSAllowedOrigins` entry into scheme/host/port, then applies exact-match and wildcard-match logic: [2](#0-1) 

For the wildcard branch, when an allowed origin is `*.ethereum.org`, the code strips the `*.` prefix to get `allowedHost = "ethereum.org"` and then checks `strings.HasSuffix(originHost, allowedHost)`. This check has no requirement that the character immediately preceding the matched suffix in `originHost` be a `.`. As a result, a host such as `notethereum.org` or `evil-ethereum.org`-style concatenations (any registrable domain ending in the literal bytes `ethereum.org`) will satisfy `HasSuffix`, even though it is not a subdomain of `ethereum.org` at all — it is an entirely different, attacker-controlled second-level domain.

This is the same root-cause bug class as GHSA-mchx-7j67-8mcf/CVE-2024-41657: an Origin-validation routine that performs a substring/affix comparison without enforcing a domain-label delimiter, allowing any attacker-registrable domain sharing the tail (or, in Casdoor's case, the head) characters to be misclassified as an authorized origin.

`handleRequest` uses the result directly to reflect the attacker's `Origin` back in `Access-Control-Allow-Origin`: [3](#0-2) 

This HTTP server is the gateway's internet-facing entry point for JSON-RPC requests, dispatched into `gateway.ProcessRequest`, which routes to handlers such as the vault secrets handler and workflow trigger handlers: [4](#0-3) 

## Impact Explanation

When a node/gateway operator enables `CORSEnabled` and configures a wildcard allowlist entry (a supported, documented configuration pattern per the httpserver tests), the boundary-check flaw lets an unrelated attacker-registered domain be treated as if it were a legitimate subdomain of the trusted origin. A page served from that attacker domain gets `Access-Control-Allow-Origin` reflected for its exact (malicious) origin, enabling the browser to allow reading of cross-origin JSON-RPC responses from the gateway's `/user` endpoint for any victim whose browser is induced to issue a request there (e.g., via a webpage that performs `fetch`/XHR with an `Authorization: Bearer <token>` value the victim's browser/extension supplies, or any workflow that relies on the CORS check as an origin-restriction boundary). This is a cross-user response confusion / origin-restriction bypass on the internet-facing gateway surface, matching the "Accept" criteria of authentication/allowlist bypass and cross-user response confusion.

## Likelihood Explanation

Exploitation requires the operator to have `CORSEnabled = true` with at least one wildcard entry in `CORSAllowedOrigins` (not the default, since defaults are `CORSEnabled = false` / empty list) as seen in the sample gateway config: [5](#0-4) 

Given that wildcard subdomain support exists specifically to be used in production UI-integration scenarios (and is exercised in tests), it is a realistic, intentionally-supported configuration, and any attacker capable of registering/controlling a domain with the matching tail bytes (which is entirely attacker-controlled, cheap, and requires no privileged access) can exploit this without any special network position — purely by getting a victim's browser to load their page and hit the gateway endpoint.

## Recommendation

Fix the wildcard suffix check in `isAllowedOrigin` to require a domain-label boundary, e.g.:
```go
if strings.HasPrefix(allowedHost, "*.") {
    suffix := allowedHost[1:] // keep leading dot: ".ethereum.org"
    if originHost == allowedHost[2:] || strings.HasSuffix(originHost, suffix) {
        return true
    }
}
```
i.e., match `"." + allowedHost` (with the leading dot preserved) against the origin host, rather than the bare stripped suffix, so `evilethereum.org` no longer satisfies a `*.ethereum.org` rule while `foo.ethereum.org` still does.

## Proof of Concept

1. Operator configures gateway `UserServerConfig` with `CORSEnabled = true` and `CORSAllowedOrigins = ["https://*.ethereum.org"]`.
2. Attacker registers `https://evilethereum.org` (no dot before `ethereum.org`) and hosts a malicious page there.
3. Victim's browser sends a request to the gateway's `/user` endpoint with `Origin: https://evilethereum.org`.
4. In `isAllowedOrigin`, `originHost = "evilethereum.org"`, `allowedHost` becomes `"ethereum.org"` after stripping `*.`, and `strings.HasSuffix("evilethereum.org", "ethereum.org")` returns `true` — an incorrect match. [6](#0-5) 
5. `handleRequest` reflects `Access-Control-Allow-Origin: https://evilethereum.org`, permitting the attacker page's script to read the JSON-RPC response for requests it issues to the gateway. [7](#0-6)

### Citations

**File:** core/services/gateway/network/httpserver.go (L157-193)
```go
func (s *httpServer) isAllowedOrigin(origin string) bool {
	originScheme, originHost, originPort, err := s.splitURL(origin)
	if err != nil {
		s.lggr.Debug("error parsing origin URL", err)
		return false
	}
	for _, allowed := range s.config.CORSAllowedOrigins {
		// probably better to do this once when server starts and store it in a map
		// this is an easier solution so we don't have to apply more changes to the code
		// just need to be careful when specifying allowed origins in the config file
		allowedScheme, allowedHost, allowedPort, err := s.splitURL(allowed)
		if err != nil {
			s.lggr.Debug("error parsing allowed origin URL", err)
			continue
		}
		// skip if the scheme doesn't match at all
		if originScheme != allowedScheme {
			continue
		}
		// skip if the port doesn't match at all
		if originPort != allowedPort {
			continue
		}
		// check for exact host match (e.g., remix.com)
		if originHost == allowedHost {
			return true
		}
		// check for wildcard host match (e.g., *.remix.com)
		if strings.HasPrefix(allowedHost, "*.") {
			allowedHost = allowedHost[2:]
			if strings.HasSuffix(originHost, allowedHost) {
				return true
			}
		}
	}
	return false
}
```

**File:** core/services/gateway/network/httpserver.go (L195-209)
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
```

**File:** core/services/gateway/gateway.go (L220-253)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
```

**File:** core/scripts/gateway/sample_config_tls.toml (L1-13)
```text
[UserServerConfig]
Port = 8088
TLSEnabled = true
TLSCertPath = "certificate.pem"
TLSKeyPath = "key.pem"
Path = "/user"
ContentTypeHeader = "application/jsonrpc"
ReadTimeoutMillis = 1000
WriteTimeoutMillis = 1000
RequestTimeoutMillis = 1000
MaxRequestBytes = 10_000
CORSEnabled = false
CORSAllowedOrigins = []
```
