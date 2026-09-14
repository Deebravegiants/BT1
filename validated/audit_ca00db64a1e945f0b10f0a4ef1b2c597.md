### Title
Incomplete hard-coded redaction blacklist in the node's HTTP request logger causes secrets/tokens to be written to logs in plaintext - (File: `core/web/router.go`)

### Summary
The Chainlink node's webserver request logger sanitizes JSON bodies and query strings before writing them to logs, but the sanitization relies on a hard-coded, incomplete blacklist of field names. Because the blacklist only matches variants of the word `"password"`, any other sensitive field name used across the API (API secrets, external‑initiator secrets/tokens, OIDC client secrets, etc.) is logged unredacted.

### Finding Description
`core/web/router.go` defines a hard-coded map used to decide which JSON body/query-string keys get redacted before being written to request logs: [1](#0-0) 

This `blacklist`/`isBlacklisted` function is used by both the JSON body sanitizer and the query-string redactor that feed the request logger: [2](#0-1) [3](#0-2) 

The blacklist only recognizes `password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`, or any key containing the substring `"password"`. It does not cover the many other credential-bearing field names used elsewhere in the same webserver:

- External Initiator credentials (`Secret`, `AccessKey`, `OutgoingSecret`, `OutgoingToken`) returned/consumed by `ExternalInitiatorsController.Create` and modeled in `bridges.ExternalInitiator` / `presenters.ExternalInitiatorAuthentication`: [4](#0-3) [5](#0-4) 
- API token fields (`APIKey`/`APISecret`) consumed via headers, and OIDC `ClientSecret` config value.
- Any user-defined job/bridge payload containing arbitrary field names like `secret`, `token`, `apiKey`, etc.

If any of these values are echoed back in a request body (e.g., during creation/edit flows) or passed as query parameters, the value would be written into node logs in cleartext because the hard-coded blacklist never matches on `secret`, `token`, `accesskey`, `apikey`, etc. — only on `password` substrings. This is exactly the "hard-coded constant, unmaintained/incomplete list" pattern called out in the external report, applied to a security-sensitive redaction path rather than a benign constant.

### Impact Explanation
Any credential or secret that is submitted via query string or JSON body under a non-"password" key name is persisted to the node's log stream in plaintext. Because logs are commonly shipped to centralized aggregators, mounted volumes, or accessible to a broader set of operators/auditors than the credential owner, this can lead to disclosure of External Initiator secrets/tokens (which grant the "Run" role and can trigger job runs) or other API secrets, enabling request impersonation or unauthorized job execution by anyone with log access, without ever needing to compromise the primary authentication path.

### Likelihood Explanation
Likelihood is moderate: it requires that a sensitive value be submitted through a request body/query string under a field name not containing "password" (which is common — e.g., `secret`, `accessKey`, `token`, `clientSecret`), combined with request/response logging being enabled at a verbosity that captures body/query content. The redaction function itself is unconditionally applied only to a fixed, narrow blacklist, so no additional exploitation steps are needed once such a request is logged.

### Recommendation
Replace the hard-coded, narrow `blacklist` map in `core/web/router.go` with a broader, explicitly documented set (or a substring/pattern based check) that also matches `secret`, `token`, `accesskey`, `apikey`, `clientsecret`, and similar sensitive-field name conventions, and add a code comment explaining the rationale/coverage so future secret-bearing fields are added deliberately rather than accidentally omitted, consistent with the linked report's guidance ("define a constant … with a clear name … add a comment").

### Proof of Concept
1. Enable webserver request/response debug logging on the node (as is common in non-default configurations).
2. Submit any authenticated API request whose JSON body or query string contains a key such as `secret`, `token`, `accessKey`, or `clientSecret` with a sensitive value (e.g., replay/resubmit an External Initiator credential in a body field named `secret`).
3. Inspect the node's log output produced via `readSanitizedJSON`/`redact` — the value is present unredacted because `isBlacklisted` only matches `password`-like keys, per `core/web/router.go:643-658`.

### Citations

**File:** core/web/router.go (L588-629)
```go
func readBody(reader io.Reader, lggr logger.Logger) string {
	buf := new(bytes.Buffer)
	_, err := buf.ReadFrom(reader)
	if err != nil {
		lggr.Warn("unable to read from body for sanitization: ", err)
		return "*FAILED TO READ BODY*"
	}

	if buf.Len() == 0 {
		return ""
	}

	s, err := readSanitizedJSON(buf)
	if err != nil {
		lggr.Warn("unable to sanitize json for logging: ", err)
		return "*FAILED TO READ BODY*"
	}
	return s
}

func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	err := json.Unmarshal(buf.Bytes(), &dst)
	if err != nil {
		return "", err
	}

	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}

	b, err := json.Marshal(cleaned)
	if err != nil {
		return "", err
	}
	return string(b), err
}
```

**File:** core/web/router.go (L631-641)
```go
func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}
```

**File:** core/web/router.go (L643-658)
```go
// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```

**File:** core/web/presenters/external_initiators.go (L12-20)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
}
```

**File:** core/bridges/external_initiator.go (L21-34)
```go
// ExternalInitiator represents a user that can initiate runs remotely
type ExternalInitiator struct {
	ID             int64
	Name           string
	URL            *models.WebURL
	AccessKey      string
	Salt           string
	HashedSecret   string
	OutgoingSecret string
	OutgoingToken  string

	CreatedAt time.Time
	UpdatedAt time.Time
}
```
