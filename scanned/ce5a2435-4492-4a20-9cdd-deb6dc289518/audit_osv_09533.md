# [C] CVE-2017-1000082

## Summary
Severity: Critical
Advisory: CVE-2017-1000082
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-1000082
Type: osv

## Details
systemd v233 and earlier fails to safely parse usernames starting with a numeric digit (e.g. "0day"), running the service in question with root privileges rather than the user intended.

## References
- http://www.securityfocus.com/bid/99507
- http://www.securitytracker.com/id/1038839
- http://www.openwall.com/lists/oss-security/2017/07/02/1
- https://github.com/systemd/systemd/issues/6237
