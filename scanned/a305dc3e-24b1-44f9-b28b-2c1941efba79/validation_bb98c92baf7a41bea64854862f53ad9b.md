## Analysis

CVE-2019-14809 is about `net/url` mishandling malformed hosts (a suffix appearing outside `Hostname()`/`Port()`), causing an authorization bypass in applications that build host-based trust decisions from a raw/parsed `Host` string. The closest analog in this codebase is the Gateway's CORS `Origin` allowlist check, which does raw string suffix matching on a `url.Parse`-derived host rather than a proper hostname-boundary comparison.

### Title
CORS Origin allowlist bypass via unanchored hostname suffix match - (File: core/services/gateway/network/httpserver.go)

### Summary
`httpServer.isAllowedOrigin` validates the `Origin` header of incoming Gateway HTTP requests against `CORSAllowedOrigins` wildcard entries (e.g. `*.remix.com`) using `strings.HasSuffix` without anchoring on a domain-label boundary, allowing an attacker-controlled origin such as `evilremix.com` to satisfy a `*.remix.com` allowlist entry.

### Finding Description
`splitURL` parses a raw origin/allowed-origin string with `url.Parse` and extracts `Host`/`Hostname()`/`Port()` [1](#0-0) . `isAllowedOrigin` then compares the request's `Origin` host against each configured allowed origin: for wildcard entries it strips the `*.` prefix and does `strings.HasSuffix(originHost, allowedHost)` with no check that the preceding character in `originHost` is a `.` (domain-label boundary) [2](#0-1) . Consequently, for an allowlist entry `*.remix.com`, any origin whose host merely ends with the string `remix.com` — e.g. `evilremix.com`, `notremix.com`, or `attacker-remix.com` — is treated as trusted, exactly the class of "hostname mishandled outside expected component" bug described by CVE-2019-14809. `handleRequest` then reflects the attacker's `Origin` back in `Access-Control-Allow-Origin` for any request that passes this check [3](#0-2) .

### Impact Explanation
An unprivileged attacker who controls a domain ending in the same suffix as an allowed wildcard host (e.g. registering `evilremix.com` when `*.remix.com` is allowlisted) can have their origin treated as trusted by the internet-facing Gateway HTTP server, bypassing the CORS allowlist restriction that operators configured to scope which frontends may call the Gateway cross-origin. This is a concrete allowlist bypass on a request path reachable by any unauthenticated client (`handleRequest` runs before any Bearer-token/JWT check) [4](#0-3) .

### Likelihood Explanation
Exploitation only requires registering/controlling a domain name with the matching suffix and setting the `Origin` header in a browser request to the Gateway; no privileged access or additional conditions are needed, and the flawed comparison (`isAllowedOrigin`) is on the hot path of every incoming request when `CORSEnabled` is true [5](#0-4) .

### Recommendation
Replace the unanchored `strings.HasSuffix` wildcard check with a boundary-safe comparison, e.g. require `originHost == allowedHost || strings.HasSuffix(originHost, "."+allowedHost)`, and consider validating hosts via `net/url`'s `Hostname()` consistently (already used elsewhere) rather than manual string splitting, to avoid any future host-mishandling class of bugs.

### Proof of Concept
1. Configure `CORSAllowedOrigins = ["https://*.remix.com"]` on the Gateway HTTP server.
2. Send a request with header `Origin: https://evilremix.com`.
3. `splitURL` yields `originHost = "evilremix.com"`; `isAllowedOrigin` strips `*.` from the allowed entry to get `"remix.com"` and evaluates `strings.HasSuffix("evilremix.com", "remix.com")`, which is `true`.
4. The server responds with `Access-Control-Allow-Origin: https://evilremix.com`, granting the attacker's origin CORS access it should not have [6](#0-5) .

### Citations

**File:** core/services/gateway/network/httpserver.go (L138-155)
```go
func (s *httpServer) splitURL(rawURL string) (string, string, string, error) {
	// lowercase the URL to avoid case sensitivity issues
	parsedURL, err := url.Parse(strings.ToLower(rawURL))
	if err != nil {
		return "", "", "", fmt.Errorf("error parsing URL: %w", err)
	}

	host, port, err := net.SplitHostPort(parsedURL.Host)
	if err != nil {
		// if there's no port, the host itself is returned
		if parsedURL.Host != "" {
			return parsedURL.Scheme, parsedURL.Host, "", nil
		}
		return "", "", "", fmt.Errorf("error splitting host and port: %w", err)
	}

	return parsedURL.Scheme, host, port, nil
}
```

**File:** core/services/gateway/network/httpserver.go (L157-234)
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
