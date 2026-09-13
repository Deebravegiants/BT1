# [C] NASA fprime-gds - Missing Authentication and Path Traversal Enable Unauthenticated RCE and Spacecraft Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-72577
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72577
Type: osv

## Details
Multiple vulnerabilities in NASA fprime-gds through 3.4.3 allow an unauthenticated remote attacker to achieve arbitrary code execution on the ground station host and inject arbitrary commands to connected spacecraft. The Flask application in src/fprime_gds/flask/app.py applies no authentication to any endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72577.json
- https://github.com/nasa/fprime-gds
- https://nvd.nist.gov/vuln/detail/CVE-2026-72577
- https://pypi.org/project/fprime-gds/
- https://github.com/nasa/fprime-gds/blob/main/src/fprime_gds/flask/commands.py
- https://github.com/nasa/fprime-gds/blob/main/src/fprime_gds/flask/updown.py
