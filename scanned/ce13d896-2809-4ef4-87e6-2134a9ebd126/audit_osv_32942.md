# [H] Epiphany: insecure external protocol invocation in epiphany

## Summary
Severity: High
Advisory: CVE-2025-3839
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-3839
Type: osv

## Details
A flaw was found in Epiphany, a tool that allows websites to open external URL handler applications with minimal user interaction. This design can be misused to exploit vulnerabilities within those handlers, making them appear remotely exploitable. The browser fails to properly warn or gate this action, resulting in potential code execution on the client device via trusted UI behavior.

## References
- https://access.redhat.com/security/cve/CVE-2025-3839
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3839.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3839
- https://bugzilla.redhat.com/show_bug.cgi?id=2361430
- https://gitlab.gnome.org/GNOME/epiphany
