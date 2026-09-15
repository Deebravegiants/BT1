No vulnerability found for this question.

The reported CVE is specific to `@apollo/server`'s `startStandaloneServer`, where the underlying Node.js HTTP body-parsing pipeline performs character-set transcoding (e.g., via `iconv-lite`) on request bodies before JSON parsing, and malicious charset declarations can trigger a CPU/memory DoS during that transcoding step.

Chainlink is a Go codebase and does not use Apollo Server or any charset-transcoding body parser. The closest analogous internet-facing HTTP endpoints are:

- The gateway HTTP server's `handleRequest`, which reads the body with `http.MaxBytesReader` and hands it directly to `handler.ProcessRequest` as raw bytes — no charset detection/transcoding occurs. [1](#0-0) 
- The local fake gateway's `parseRequest`, which similarly does `io.ReadAll` bounded by `http.MaxBytesReader` followed by `json.Unmarshal`. [2](#0-1) 
- The GraphQL scalar handling in `core/web/gqlscalar/map.go`, which relies on Go's standard `encoding/json`, which only ever decodes UTF-8 and does not perform iconv-style charset transcoding. [3](#0-2) 

None of these paths perform character-set sniffing or transcoding of the request body prior to JSON parsing — that specific mechanism (multi-charset transcoding library invoked based on `Content-Type` charset parameter) is what enables the Apollo Server DoS, and it has no equivalent in Go's `net/http` + `encoding/json` stack used here. Go's `encoding/json.Unmarshal` strictly expects UTF-8 and will simply error out on other encodings rather than attempting expensive transcoding. All examined ingress paths already enforce byte-size limits via `http.MaxBytesReader` before any parsing occurs, which further mitigates unbounded resource consumption from oversized or malformed payloads. [4](#0-3) 

Since the root-cause mechanism (charset transcoding prior to JSON parsing) does not exist anywhere in this codebase's unprivileged-facing HTTP/GraphQL handling, there is no valid analog to this vulnerability class.

### Citations

**File:** core/services/gateway/network/httpserver.go (L211-234)
```go
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

**File:** core/capabilities/fakes/gateway/local.go (L100-117)
```go
func parseRequest(req *http.Request) ([]byte, error) {
	if req.Method != http.MethodPost {
		return nil, errors.New("gateway expects POST request")
	}
	defer req.Body.Close()

	body, err := io.ReadAll(http.MaxBytesReader(nil, req.Body, maxRequestBytes))
	if err != nil {
		return nil, fmt.Errorf("read request body: %w", err)
	}

	var request triggerRequest
	if err := json.Unmarshal(body, &request); err != nil {
		return nil, fmt.Errorf("parse request body: %w", err)
	}

	return request.Input, nil
}
```

**File:** core/web/gqlscalar/map.go (L1-33)
```go
package gqlscalar

import (
	"encoding/json"

	"github.com/pkg/errors"
)

// Map to contain configuration
type Map map[string]any

// ImplementsGraphQLType implements GraphQL type for Map
func (Map) ImplementsGraphQLType(name string) bool { return name == "Map" }

// UnmarshalGraphQL sets the Map
func (m *Map) UnmarshalGraphQL(input any) error {
	switch input := input.(type) {
	case Map:
		*m = input
		return nil
	default:
		return errors.New("wrong type")
	}
}

// MarshalJSON returns json
func (m Map) MarshalJSON() ([]byte, error) {
	// Cast this so we don't have infinite recursion
	// (don't want json.Marshal calling the MarshalJSON method on m)
	return json.Marshal(map[string]any(m))
}


```
