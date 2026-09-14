### Title
Log spoofing via unsanitized `\n`/`\r`/`\t` in unprivileged client-supplied identifiers rendered by the pretty console log formatter - ([File: core/logger/prettyconsole.go])

### Summary
The `sanitized.String()` helper used by `PrettyConsole.Write` explicitly **allows** `\n`, `\r`, and `\t` to pass through unescaped when rendering log field values (`msg`, and every key/value pair in `generateDetails`), while escaping all other control characters. [1](#0-0)  This is the same bug class as CVE-2022-23949 (unsanitized identifiers from an untrusted actor causing log spoofing): any field containing an attacker-supplied identifier that reaches this formatter can inject fake, attacker-crafted log lines/fields into the human-readable console/log output.

### Finding Description
`PrettyConsole.Write` parses each JSON log line with `gjson` and re-renders it as `headline` + `details` for console/file output. [2](#0-1)  The `sanitized` type is meant to neutralize control characters in log values, but its `switch` explicitly special-cases `\n`, `\r`, `\t` as "allowed" and only escapes other control characters. [3](#0-2)  Both `generateHeadline` (the `msg` field) and `generateDetails` (every other field, including keys and values) route strings through `sanitized(...)`. [4](#0-3) 

Multiple internet-facing and unprivileged-actor-controlled identifiers are logged verbatim through structured logger calls that ultimately reach this formatter, e.g.:
- Gateway JSON-RPC `req.ID` (an unprivileged HTTP client field, length-capped at 200 chars but not content-filtered for control characters) is logged directly: `g.lggr.Debugw(... "requestID", jsonRequest.ID)` [5](#0-4) , and again in the vault/confidential-relay gateway handlers, e.g. `h.requestLogger(req, gatewayID)` building `"requestID", req.ID` fields. [6](#0-5) 
- `requestLabels.WorkflowID` / `ExecutionID` decoded straight from user-supplied JSON `params` and logged. [7](#0-6) 
- HTTP trigger request IDs are only checked for emptiness and the `/` character, not for control characters, before being logged in error paths. [8](#0-7) 

When the node is run with `JSONConsole = false` (the documented default, human-readable console mode), these strings flow through `pretty://console` → `PrettyConsole.Write` → `sanitized.String()`, where embedded `\n`/`\r` are preserved verbatim in the rendered output. [9](#0-8) [10](#0-9)  An unprivileged caller can thus embed newline-delimited, forged log lines (fake timestamps, levels, or messages) inside an identifier such as a gateway `requestID` or a workflow/execution ID, and have them rendered as if they were genuine log entries in the node operator's console/log file — this is functionally the same "unsanitized-ID log-spoofing" defect as CVE-2022-23949, just realized in the pretty-console renderer rather than at the point of construction.

Note: when `JSONConsole = true` the underlying encoder is `zapcore.NewJSONEncoder`, which correctly JSON-escapes `\n`/`\r` as `\n`/`\r` (JSON string escaping is applied by the encoder before this pretty-print step runs, so JSON-mode file output is not affected). [11](#0-10)  The vulnerable path is specifically the pretty/human-readable console renderer, which is the default configuration (`JSONConsole = false`). [10](#0-9) 

Notably, elsewhere in the codebase (`core/capabilities/remote/utils.go`), the project already implements a stricter `SanitizeLogString` that rejects any non-printable rune (including `\n`) and hex-encodes the whole string instead, precisely to prevent this class of injection for P2P message fields. [12](#0-11)  That protection is not applied to gateway/user-facing request IDs, workflow/execution IDs, or other unprivileged-client-controlled fields, and the pretty-console formatter's own sanitizer intentionally whitelists the exact characters needed for line-injection.

### Impact Explanation
This enables a network-facing, unprivileged actor (any client hitting the gateway's JSON-RPC endpoint, or an external initiator/API caller supplying identifiers that get logged) to inject arbitrary forged lines into a node operator's console output or log files. This can be used to: fabricate misleading operational/audit trails, hide evidence of real malicious activity by pushing it out of view or overwriting apparent context, or trigger confusion during incident response (the exact impact described by the Keylime CVE — log spoofing that misleads an operator/verifier). It does not directly grant privilege escalation, secret disclosure, or fund movement, which keeps it at a moderate rather than critical severity, consistent with the "High" (not Critical) rating of the analogous CVE.

### Likelihood Explanation
Reaching this code path requires no privilege: an unprivileged actor need only issue a normal gateway JSON-RPC request (or any request whose identifier fields are echoed into logs) with an ID/workflow-ID/execution-ID containing `\n`/`\r` characters. Length caps (200 chars) exist on some IDs but do not block control characters, and the `/`-character check on HTTP trigger request IDs does not block newlines either. The main precondition is that the node operator uses the default human-readable console logging mode (`JSONConsole = false`), which is the documented default.

### Recommendation
Update `sanitized.String()` in `core/logger/prettyconsole.go` to escape `\n`, `\r`, and `\t` like any other control character (or route them through `strconv.QuoteRune` the same way non-listed control characters are handled), removing the special-case "allowed" branch. Alternatively/additionally, apply the existing `remote.SanitizeLogString`-style whitelist-of-printable-characters approach to all externally supplied identifiers (gateway `req.ID`, workflow/execution IDs, HTTP trigger request IDs, external-initiator names) before they are attached as log fields anywhere in the gateway/API layer.

### Proof of Concept
1. Run a chainlink node with default config (`JSONConsole = false`, i.e., pretty console logging).
2. As an unprivileged client, send a gateway JSON-RPC request with an `id` (or a workflow/execution ID embedded in `params`) such as:
   `"id": "legituser\n2026-09-14T00:00:00Z [CRIT]  fake critical error: wallet drained by user X caller=fake.go:1 "`
3. The gateway logs this value via `"requestID", jsonRequest.ID` (`core/services/gateway/gateway.go:292`) or via `requestLabels` fields (`core/services/gateway/handlers/confidentialrelay/handler.go:85-107`).
4. `PrettyConsole.Write` renders the JSON log entry; `generateDetails`/`sanitized.String()` passes the embedded `\n` through unescaped, causing the forged text after the `\n` to appear on its own console/log line, indistinguishable from a genuine entry produced by the node itself. [13](#0-12)

### Citations

**File:** core/logger/prettyconsole.go (L42-50)
```go
func (pc PrettyConsole) Write(b []byte) (int, error) {
	if !gjson.ValidBytes(b) {
		return 0, fmt.Errorf("unable to parse json for pretty console: %s", string(b))
	}
	js := gjson.ParseBytes(b)
	headline := generateHeadline(js)
	details := generateDetails(js)
	return pc.Sink.Write(fmt.Appendln(nil, headline, details))
}
```

**File:** core/logger/prettyconsole.go (L73-156)
```go
	headline := []any{
		tsStr,
		" ",
		coloredLevel(js.Get("level")),
		fmt.Sprintf("%-50s", sanitized(js.Get("msg").String())),
		" ",
		fmt.Sprintf("%-32s", blue(js.Get("caller"))),
	}
	return fmt.Sprint(headline...)
}

// detailsBlacklist of keys to show in details. This does not
// exclude it from being present in other logger sinks, like .jsonl files.
var detailsBlacklist = map[string]bool{
	"level":  true,
	"ts":     true,
	"msg":    true,
	"caller": true,
	"hash":   true,
}

func generateDetails(js gjson.Result) string {
	data := js.Map()
	keys := []string{}

	for k := range data {
		if detailsBlacklist[k] || len(data[k].String()) == 0 {
			continue
		}
		keys = append(keys, k)
	}

	sort.Strings(keys)

	var details strings.Builder

	for _, v := range keys {
		fmt.Fprintf(&details, "%s=%v ", green(sanitized(v)), sanitized(data[v].String()))
	}

	return details.String()
}

func coloredLevel(level gjson.Result) string {
	color, ok := levelColors[level.String()]
	if !ok {
		color = levelColors["default"]
	}
	return color(fmt.Sprintf("%-8s", fmt.Sprint("[", strings.ToUpper(level.String()), "]")))
}

// iso8601UTC formats given time to ISO8601.
func iso8601UTC(t time.Time) string {
	return t.UTC().Format(time.RFC3339)
}

func prettyConsoleSink(s zap.Sink) func(*url.URL) (zap.Sink, error) {
	return func(*url.URL) (zap.Sink, error) {
		return PrettyConsole{s}, nil
	}
}

type sanitized string

// String replaces control characters with Go escape sequences, except for newlines and tabs.
// See strconv.QuoteRune.
func (s sanitized) String() string {
	var out strings.Builder
	for _, r := range s {
		switch r {
		case '\n', '\r', '\t':
			// allowed
		default:
			// escape others
			if unicode.IsControl(r) {
				q := strconv.QuoteRune(r)
				out.WriteString(q[1 : len(q)-1]) // trim quotes
				continue
			}
		}
		out.WriteRune(r)
	}
	return out.String()
}
```

**File:** core/services/gateway/gateway.go (L292-293)
```go
	g.lggr.Debugw("received response from handler", "handler", handlerKey, "response", response, "requestID", jsonRequest.ID)
	promRequest.WithLabelValues(response.ErrorCode.String()).Inc()
```

**File:** core/capabilities/vault/gw_handler.go (L176-182)
```go
func (h *GatewayHandler) requestLogger(req *jsonrpc.Request[json.RawMessage], gatewayID string) logger.Logger {
	return h.lggr.With("requestID", req.ID, "method", req.Method, "gatewayID", gatewayID)
}

func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L84-107)
```go
type requestLabels struct {
	WorkflowID  string `json:"workflow_id"`
	ExecutionID string `json:"execution_id"`
}

// extractRequestLabels best-effort decodes the logging identifiers from a
// request's params. Both relay methods' params carry these fields. A decode
// failure leaves them empty and is only logged: these labels are for
// correlation, and the params themselves are validated by the relay nodes,
// not here, so a request whose params do not decode is still fanned out and
// rejected there. ProcessRequest has already parsed the envelope as valid
// JSON by this point, so a failure here means params is not an object or
// carries non-string identifiers — malformed input rather than a gateway bug,
// hence debug level to avoid handing a caller a log-spam lever.
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
	if err := json.Unmarshal(*req.Params, &labels); err != nil {
		h.lggr.Debugw("could not decode relay request params for logging labels",
			"method", req.Method, "requestID", req.ID, "err", err)
	}
	return labels
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-202)
```go
func (h *httpTriggerHandler) validateRequestID(ctx context.Context, requestID string, callback handlers.Callback) error {
	if requestID == "" {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "'id' field is required and cannot be empty. Use a new unique request 'id' for each request", callback)
		return errors.New("empty request ID")
	}
	// Request IDs from users must not contain "/", since this character is reserved
	// for internal node-to-node message routing (e.g., "http_action/{workflowID}/{uuid}").
	if strings.Contains(requestID, "/") {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "request ID must not contain '/'", callback)
		return errors.New("request ID must not contain '/'")
	}
	return nil
}
```

**File:** core/logger/logger.go (L136-145)
```go
func newZapConfigProd(jsonConsole bool, unixTS bool) zap.Config {
	config := newZapConfigBase()
	if !unixTS {
		config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	}
	if !jsonConsole {
		config.OutputPaths = []string{"pretty://console"}
	}
	return config
}
```

**File:** core/logger/logger.go (L285-300)
```go
func newDefaultLoggingCore(zcfg zap.Config, unixTS bool) (zapcore.Core, func(), error) {
	encoder := zapcore.NewJSONEncoder(makeEncoderConfig(unixTS))

	sink, closeOut, err := zap.Open(zcfg.OutputPaths...)
	if err != nil {
		return nil, nil, err
	}

	if zcfg.Level == (zap.AtomicLevel{}) {
		return nil, nil, errors.New("missing Level")
	}

	filteredLogLevels := zap.LevelEnablerFunc(zcfg.Level.Enabled)

	core := zapcore.NewCore(encoder, sink, filteredLogLevels)
	return core, closeOut, nil
```

**File:** core/config/docs/core.toml (L152-153)
```text
# JSONConsole enables JSON logging. Otherwise, the log is saved in a human-friendly console format.
JSONConsole = false # Default
```

**File:** core/capabilities/remote/utils.go (L58-70)
```go
func SanitizeLogString(s string) string {
	tooLongSuffix := ""
	if len(s) > maxLoggedStringLen {
		s = s[:maxLoggedStringLen]
		tooLongSuffix = " [TRUNCATED]"
	}
	for i := range len(s) {
		if !unicode.IsPrint(rune(s[i])) {
			return "[UNPRINTABLE] " + hex.EncodeToString([]byte(s)) + tooLongSuffix
		}
	}
	return s + tooLongSuffix
}
```
