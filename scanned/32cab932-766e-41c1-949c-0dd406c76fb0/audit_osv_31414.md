# [H] Foreman: os command injection via ct_location and fcct_location parameters

## Summary
Severity: High
Advisory: CVE-2025-10622
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-10622
Type: osv

## Details
A flaw was found in Red Hat Satellite (Foreman component). This vulnerability allows an authenticated user with edit_settings permissions to achieve arbitrary command execution on the underlying operating system via insufficient server-side validation of command whitelisting.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://theforeman.org/security.html#2025-10622
- https://access.redhat.com/errata/RHSA-2025:19721
- https://access.redhat.com/errata/RHSA-2025:19832
- https://access.redhat.com/errata/RHSA-2025:19855
- https://access.redhat.com/errata/RHSA-2025:19856
- https://access.redhat.com/security/cve/CVE-2025-10622
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10622.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10622
- https://bugzilla.redhat.com/show_bug.cgi?id=2396020
- https://github.com/theforeman/foreman
