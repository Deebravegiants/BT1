# [C] Samba: samba: remote code execution in printing subsystem via unescaped job description

## Summary
Severity: Critical
Advisory: CVE-2026-4480
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-4480
Type: osv

## Details
A flaw was found in the Samba printing subsystem. Samba passes the client-controlled job description string to the command configured with the "print command" setting via the "%J"
substitution character without escaping shell meta characters. A remote attacker could exploit this vulnerability by sending a specially crafted print job description that contains unescaped shell characters. This could lead to remote code execution on the affected system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4480.json
- https://access.redhat.com/errata/RHSA-2026:22644
- https://access.redhat.com/errata/RHSA-2026:22963
- https://access.redhat.com/errata/RHSA-2026:25049
- https://access.redhat.com/errata/RHSA-2026:25979
- https://access.redhat.com/errata/RHSA-2026:28053
- https://access.redhat.com/errata/RHSA-2026:28054
- https://access.redhat.com/errata/RHSA-2026:28055
- https://access.redhat.com/errata/RHSA-2026:28056
- https://access.redhat.com/errata/RHSA-2026:28057
- https://access.redhat.com/errata/RHSA-2026:28058
- https://access.redhat.com/errata/RHSA-2026:28132
- https://access.redhat.com/security/cve/CVE-2026-4480
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4480.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4480
- https://bugzilla.redhat.com/show_bug.cgi?id=2452232
- https://bugzilla.samba.org/show_bug.cgi?id=16033
