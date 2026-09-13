# [C] alseambusher crontab-ui - Unauthenticated RCE via Shell Injection in Imported Database hook Field

## Summary
Severity: Critical
Advisory: CVE-2026-72589
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72589
Type: osv

## Details
An OS command injection vulnerability in alseambusher/crontab-ui through 0.4.2 allows an unauthenticated remote attacker to execute arbitrary system commands by importing a crafted crontab database file. The POST /import endpoint accepts arbitrary .db files and overwrites the application database without validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72589.json
- https://github.com/alseambusher/crontab-ui
- https://nvd.nist.gov/vuln/detail/CVE-2026-72589
- https://github.com/alseambusher/crontab-ui/blob/master/crontab.js
