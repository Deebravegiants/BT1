# [M] CVE-2023-2019

## Summary
Severity: Medium
Advisory: CVE-2023-2019
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-2019
Type: osv

## Details
A flaw was found in the Linux kernel's netdevsim device driver, within the scheduling of events. This issue results from the improper management of a reference count. This may allow an attacker to create a denial of service condition on the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2019.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2019
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-17811/
- https://bugzilla.redhat.com/show_bug.cgi?id=2189137
- https://github.com/torvalds/linux/commit/180a6a3ee60a
