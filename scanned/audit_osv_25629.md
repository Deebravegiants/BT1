# [M] Shim: out-of-bounds read printing error messages

## Summary
Severity: Medium
Advisory: CVE-2023-40546
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/CVE-2023-40546
Type: osv

## Details
A flaw was found in Shim when an error happened while creating a new ESL variable. If Shim fails to create the new variable, it tries to print an error message to the user; however, the number of parameters used by the logging function doesn't match the format string used by it, leading to a crash under certain circumstances.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/05/msg00009.html
- https://access.redhat.com/errata/RHSA-2024:1834
- https://access.redhat.com/errata/RHSA-2024:1835
- https://access.redhat.com/errata/RHSA-2024:1873
- https://access.redhat.com/errata/RHSA-2024:1876
- https://access.redhat.com/errata/RHSA-2024:1883
- https://access.redhat.com/errata/RHSA-2024:1902
- https://access.redhat.com/errata/RHSA-2024:1903
- https://access.redhat.com/errata/RHSA-2024:1959
- https://access.redhat.com/errata/RHSA-2024:2086
- https://access.redhat.com/security/cve/CVE-2023-40546
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40546.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40546
- https://bugzilla.redhat.com/show_bug.cgi?id=2241796
