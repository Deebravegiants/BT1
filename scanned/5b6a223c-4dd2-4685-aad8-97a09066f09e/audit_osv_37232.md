# [H] CVE-2026-3006

## Summary
Severity: High
Advisory: CVE-2026-3006
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-3006
Type: osv

## Details
Successful exploitation of the race condition vulnerability could allow
an attacker to trigger a kernel heap overflow, potentially leading to local privilege
escalation and granting system-level access to the affected software.

## References
- https://access.redhat.com/security/cve/CVE-2026-3006
- https://github.com/winfsp/winfsp/releases/tag/v2.2B1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3006.json
- https://www.csa.gov.sg/alerts-and-advisories/alerts/al-2026-043
- https://bugzilla.redhat.com/show_bug.cgi?id=2463150
