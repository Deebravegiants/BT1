# [M] Libsolv: heap buffer overflow in libsolv repo_add_solv via negative maxsize from crafted .solv file

## Summary
Severity: Medium
Advisory: CVE-2026-9149
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-9149
Type: osv

## Details
A flaw was found in libsolv. This heap buffer overflow vulnerability occurs when a victim processes a specially crafted `.solv` file containing negative size values in the `repo_add_solv` function. This leads to an undersized memory allocation and a subsequent out-of-bounds write. An attacker could exploit this to cause a denial of service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:21333
- https://access.redhat.com/errata/RHSA-2026:28236
- https://access.redhat.com/errata/RHSA-2026:48818
- https://access.redhat.com/security/cve/CVE-2026-9149
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9149.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9149
- https://bugzilla.redhat.com/show_bug.cgi?id=2460380
- https://github.com/openSUSE/libsolv/pull/617
