# [C] CVE-2021-44458

## Summary
Severity: Critical
Advisory: CVE-2021-44458
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-44458
Type: osv

## Details
Linux users running Lens 5.2.6 and earlier could be compromised by visiting a malicious website. The malicious website could make websocket connections from the victim's browser to Lens and so operate the local terminal feature. This would allow the attacker to execute arbitrary commands as the Lens user.

## References
- https://github.com/Mirantis/security/blob/main/advisories/0001.md
