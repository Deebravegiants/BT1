Based on my investigation, the strongest reachable analog is the audit logger's `CreateSession` path, which serializes and forwards WebAuthn credential data as part of successful-login audit events.

### Title
Audit Logger Forwards User WebAuthn Public-Key Credential Blob in Plaintext Audit Events - (File: core/sessions/localauth/orm.go)

### Summary
`orm.CreateSession` marshals the full set of a user's registered WebAuthn credential records (`uwas`) to JSON and attaches it under the `"credential"` key of the `AuthLoginSuccessWith2FA` audit event, which is then queued and forwarded off-node to a configured HTTP endpoint by the audit logger.

### Finding Description
After a successful MFA login, `orm.CreateSession` marshals `uwas []sessions.WebAuthn` (each containing `PublicKeyData sqlxTypes.JSONText`, itself a serialized `webauthn.Credential`) and passes it as event data: [1](#0-0) . This flows into `AuditLoggerService.Audit`, which queues the event and later serializes and POSTs it in full to the operator-configured `ForwardToUrl` endpoint via `postLogToLogService`: [2](#0-1) [3](#0-2) . This is directly analogous to the RustFS pattern of writing full credential/session structures into log sinks: the code embeds a JSON-serialized security-credential structure rather than a redacted identifier into a structured log/audit record that leaves the process boundary.

The `webauthn.Credential` structure stored in `PublicKeyData` (unmarshaled/marshaled elsewhere, e.g. `core/sessions/webauthn.go:210-217,283-293`) contains the WebAuthn credential ID and authenticator public key/attestation data used to authenticate the user via FIDO2/WebAuthn. While this is not a symmetric secret like a password or API secret key, the credential ID is a long-lived, non-rotatable authenticator identifier that is normally treated as sensitive, and forwarding it in bulk to an external, potentially less-trusted log-forwarding endpoint increases its exposure surface beyond what is needed for auditing (an audit event does not need to embed the entire raw credential set — only a non-sensitive identifier or count would suffice).

### Impact Explanation
Impact is limited: this is a public-key/attestation record, not a symmetric secret like RustFS's `secret_key`/`session_token`. Compromise via the forwarded audit log requires access to the configured external log-forwarding endpoint's network path or storage, and even then the attacker gains a WebAuthn credential ID/public key blob, not a usable bearer credential (there is no private key material here since WebAuthn keeps private keys on the authenticator device). This differentiates it materially from the RustFS report, where the leaked material (secret_key, session_token) was directly usable to authenticate.

### Likelihood Explanation
Likelihood of this specific data reaching an untrusted party is low: it requires the `AuditLogger` to be `Enabled=true` with a `ForwardToUrl` configured (opt-in, operator-controlled) and a successful MFA login flow to occur, and then requires the log-forwarding channel/destination itself to be compromised or over-broadly accessible. There is no unprivileged-attacker path to directly force this disclosure remotely; it depends on operator's own audit pipeline security.

### Recommendation
Do not include the full `uwas` JSON blob in audit event data. Replace with non-sensitive identifiers only (e.g., credential ID count or a boolean indicating MFA was used), matching the RustFS remediation guidance of logging safe identifiers instead of full credential material: `map[string]any{"email": sr.Email}` (as already done for the No-2FA path) rather than `map[string]any{"email": sr.Email, "credential": string(uwasj)}`.

### Proof of Concept
1. Enable `[AuditLogger] Enabled = true` with `ForwardToUrl` pointing at an attacker-observable or under-monitored HTTP endpoint (a realistic misconfiguration/insider-threat scenario, not requiring code-level privilege).
2. Register WebAuthn/MFA for a user account.
3. As that user, log in successfully with valid WebAuthn attestation via the `/sessions` endpoint (`SessionCookieAuthenticator.Authenticate` → `orm.CreateSession`): [4](#0-3) .
4. Observe the `AUTH_LOGIN_SUCCESS_WITH_2FA` audit event delivered to `ForwardToUrl` contains the full serialized `credential` JSON blob (WebAuthn credential ID + public key data) rather than a redacted/minimal identifier: [1](#0-0) .

### Citations

**File:** core/sessions/localauth/orm.go (L221-227)
```go
	// Forward registered credentials for audit logs
	uwasj, err := json.Marshal(uwas)
	if err != nil {
		lggr.Errorf("error in Marshal credentials: %s", err)
	} else {
		o.auditLogger.Audit(audit.AuthLoginSuccessWith2FA, map[string]any{"email": sr.Email, "credential": string(uwasj)})
	}
```

**File:** core/logger/audit/audit_logger.go (L121-136)
```go
func (l *AuditLoggerService) Audit(eventID EventID, data Data) {
	if !l.enabled {
		return
	}

	wrappedLog := wrappedAuditLog{
		eventID: eventID,
		data:    data,
	}

	select {
	case l.loggingChannel <- wrappedLog:
	default:
		l.logger.Errorf("buffer is full. Dropping log with eventID: %s", eventID)
	}
}
```

**File:** core/logger/audit/audit_logger.go (L207-226)
```go
func (l *AuditLoggerService) postLogToLogService(eventID EventID, data Data) {
	// Audit log JSON data
	logItem := map[string]any{
		"eventID":  eventID,
		"hostname": l.hostname,
		"localIP":  l.localIP,
		"env":      l.environmentName,
		"data":     data,
	}

	// Optionally wrap audit log data into JSON object to help dynamically structure for an HTTP log service call
	if l.jsonWrapperKey != "" {
		logItem = map[string]any{l.jsonWrapperKey: logItem}
	}

	serializedLog, err := json.Marshal(logItem)
	if err != nil {
		l.logger.Errorw("unable to serialize wrapped audit log item to JSON", "err", err, "logItem", logItem)
		return
	}
```

**File:** core/cmd/shell.go (L720-744)
```go
// Authenticate retrieves a session ID via a cookie and saves it to disk.
func (t *SessionCookieAuthenticator) Authenticate(ctx context.Context, sessionRequest sessions.SessionRequest) (*http.Cookie, error) {
	b := new(bytes.Buffer)
	err := json.NewEncoder(b).Encode(sessionRequest) //nolint:gosec // SessionRequest.Password is the login payload, not a leaked secret
	if err != nil {
		return nil, err
	}
	url := t.config.RemoteNodeURL.String() + "/sessions"
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, b)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	client := newHTTPClient(t.lggr, t.config.InsecureSkipVerify)
	resp, err := client.Do(req) //nolint:bodyclose // closed via defer t.lggr.ErrorIfFn below
	if err != nil {
		return nil, err
	}
	defer t.lggr.ErrorIfFn(resp.Body.Close, "Error closing Authenticate response body")

	_, err = parseResponse(resp)
	if err != nil {
		return nil, err
	}
```
