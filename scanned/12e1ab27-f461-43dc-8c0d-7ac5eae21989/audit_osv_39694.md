# [H] CVE-2026-46581

## Summary
Severity: High
Advisory: CVE-2026-46581
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-46581
Type: osv

## Details
In Eclipse Mojarra versions 2.3 and following, URL handing in `DefaultFaceletFactory` does not properly sanitize and/or block remote URLs, allowing an attacker to specify a URL to a remote Facelet which will be included and processed as part of the normal request, with the privileges of the target server. This could allow access to restricted files such as `WEB-INF/web.xml` or `/etc/passwd`.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/160
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46581.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46581
