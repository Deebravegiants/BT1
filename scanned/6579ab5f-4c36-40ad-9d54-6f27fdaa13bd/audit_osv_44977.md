# [M] Libsolv: stack-based buffer overflow in libsolv's debian metadata parser when handling sha384/sha512 checksums

## Summary
Severity: Medium
Advisory: CVE-2026-9150
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-9150
Type: osv

## Details
A flaw was found in libsolv. This stack-based buffer overflow vulnerability occurs in libsolv's Debian metadata parser when processing specially crafted Debian repository metadata. An attacker could exploit this by providing malicious SHA384 or SHA512 checksum tags, leading to memory corruption and a denial of service (DoS) in the affected system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:21333
- https://access.redhat.com/errata/RHSA-2026:28236
- https://access.redhat.com/errata/RHSA-2026:30649
- https://access.redhat.com/errata/RHSA-2026:48818
- https://access.redhat.com/security/cve/CVE-2026-9150
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9150.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9150
- https://bugzilla.redhat.com/show_bug.cgi?id=2460379
- https://github.com/openSUSE/libsolv/pull/616
