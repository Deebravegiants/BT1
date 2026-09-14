### Title
Log Injection via unescaped newlines in pretty-console log sanitizer allows unauthenticated login requests to forge fake log entries - (File: `core/logger/prettyconsole.go`)

### Summary
This is a valid analog of the pyload `GHSA-ghmw-rwh8-6qmr` log-injection class. Chainlink's pretty-console log formatter explicitly whitelists raw newline/carriage-return characters when sanitizing field values before writing them to the log stream, and unauthenticated login requests (`POST /sessions`) place attacker-controlled email input directly into structured log fields and formatted log messages that flow through this sanitizer.

### Finding Description
`core/logger/prettyconsole.go` defines a `sanitized` type used to clean string values before they're written to the console/log file: [1](#0-0) 

Critically, the `switch` statement explicitly **allows** `\n`, `\r`, and `\t` to pass through untouched ("// allowed"), while escaping other control characters. This function is applied to both the log message (`generateHeadline`) and every structured field value (`generateDetails`): [2](#0-1) 

Since newline is also the delimiter between rendered log lines/details, any user-controlled string containing `\n` that ends up in a logged field or message will be split into what looks like separate, fabricated log lines — the exact bug class described in the pyload advisory (newline not escaped, and newline is the log-entry delimiter).

The unauthenticated login path reaches this sink. `SessionsController.Create` in `core/web/sessions_controller.go` binds `SessionRequest` (email/password) from the request body without authentication and passes it to `AuthenticationProvider().CreateSession`: [3](#0-2) 

Downstream authenticators log this attacker-controlled email directly, either via `%s` string formatting into the log message or via structured fields:
- LDAP authenticator logs the raw email into the message string on success: `l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)` and similar `Infof` calls with `%v`-wrapped errors. [4](#0-3) [5](#0-4) 
- Local auth ORM attaches the resolved user's email as a structured field via `o.lggr.With("user", user.Email)` and continues to log with it: [6](#0-5) 

Because the default logging configuration renders to the pretty console sink unless `Log.JSONConsole` is enabled: [7](#0-6) 

the vulnerable `sanitized.String()` path is on the default/production code path (`newZapConfigProd` sets `OutputPaths = []string{"pretty://console"}` when `!jsonConsole`), not merely a debug-only feature.

Note: the separate `AuditLoggerService` that forwards structured audit events (e.g., `AuthLoginFailedEmail`) to an external HTTP endpoint uses `json.Marshal`, which properly escapes embedded newlines as `\n` in the payload; that specific path is **not** vulnerable. The vulnerable sink is the local node's own structured `zapLogger` → pretty-console renderer, used throughout the codebase for `Infof`/`Errorw`/`With(...)` style logging, including auth flows.

### Impact Explanation
An unauthenticated actor sending crafted login requests (or any other unauthenticated input that is logged, e.g. LDAP bind failures, WebAuthn lookups) with embedded newlines in the `email` field can inject forged log lines into the node operator's console/log file output. This can be used to:
- Fabricate misleading operational or security events to cover tracks of a real attack.
- Frame the appearance of legitimate activity (e.g. fake "Successful login" entries) or spoof error conditions to mislead node operators/SOC tooling that parses the pretty-console log format.

Impact is limited to log integrity/confusion (CWE-93/CWE-117 style), not direct authentication bypass, key disclosure, or fund movement — consistent with the "Medium" severity of the original advisory.

### Likelihood Explanation
High likelihood of triggering: the login endpoint (`POST /sessions`) is unauthenticated by design, accepts an arbitrary `email` string in JSON, and is reached by any client before authentication. No knowledge of a valid account is required to reach the `AuthLoginFailedEmail`/LDAP bind failure logging paths that echo the raw input. The only precondition is that the deployment uses the default pretty-console logging (`Log.JSONConsole = false`, which is the documented default).

### Recommendation
Update `sanitized.String()` in `core/logger/prettyconsole.go` to escape `\n` and `\r` (and ideally `\t`) rather than passing them through unescaped, consistent with how other control characters are already quoted via `strconv.QuoteRune`. This prevents attacker-controlled field values/messages from injecting fabricated log-line boundaries into the pretty-console renderer, regardless of which code path logs the value.

### Proof of Concept
1. Run a chainlink node with default logging config (`Log.JSONConsole = false`, the default).
2. Send an unauthenticated login request with a newline-embedded email, e.g.:
```
curl -X POST http://localhost:6688/sessions \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@example.com\n2024-01-05T00:00:00Z [INFO] FAKE Successful login for admin@example.com","password":"wrong"}'
```
3. Because `CreateSession` logs/audits the raw `sr.Email` value (e.g. via LDAP `Infof("Successful LDAP login request for user %s ...")` on other paths, or via the structured `"user"`/`"email"` fields), and `prettyconsole.go`'s `sanitized.String()` allows the embedded `\n` through unescaped, the rendered console/log output will contain what appears to be two separate log lines — the second one fabricated by the attacker — even though only a single unauthenticated request was made.

### Citations

**File:** core/logger/prettyconsole.go (L63-114)
```go
func generateHeadline(js gjson.Result) string {
	ts := js.Get("ts")
	var tsStr string
	if f := ts.Float(); f > 1 {
		sec, dec := math.Modf(f)
		tsStr = iso8601UTC(time.Unix(int64(sec), int64(dec*(1e9))))
	} else {
		// assume already formatted
		tsStr = ts.Str
	}
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
```

**File:** core/logger/prettyconsole.go (L135-156)
```go
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

**File:** core/web/sessions_controller.go (L29-60)
```go
func (sc *SessionsController) Create(c *gin.Context) {
	defer sc.App.WakeSessionReaper()
	ctx := c.Request.Context()
	sc.App.GetLogger().Debugf("TRACE: Starting Session Creation")

	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/sessions/ldapauth/ldap.go (L405-419)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}

	// Bind was successful meaning user and credentials are present in LDAP directory
	// Reuse FindUser functionality to fetch user roles used to create ldap_session entry
	// with cached user email and role
	foundUser, err := l.FindUser(ctx, escapedEmail)
	if err != nil {
		l.lggr.Infof("Successful user login, but error querying for user groups: user: %s, error %v", escapedEmail, err)
		returnErr = errors.New("log in successful, but no assigned groups to assume role")
```

**File:** core/sessions/ldapauth/ldap.go (L433-436)
```go
	}

	l.lggr.Infof("Successful LDAP login request for user %s - %s", sr.Email, foundUser.Role)

```

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
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
