# [C] alseambusher crontab-ui - Unauthenticated RCE via Newline Injection in env_vars Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-72590
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72590
Type: osv

## Details
An OS command injection vulnerability in alseambusher/crontab-ui through 0.4.2 allows an unauthenticated remote attacker to inject arbitrary cron job entries by sending a crafted GET request to /crontab with URL-encoded newlines in the env_vars parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72590.json
- https://github.com/alseambusher/crontab-ui
- https://nvd.nist.gov/vuln/detail/CVE-2026-72590
- https://github.com/alseambusher/crontab-ui/blob/master/app.js
