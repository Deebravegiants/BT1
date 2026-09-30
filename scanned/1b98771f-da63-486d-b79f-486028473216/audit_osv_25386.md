# [M] DataEase has a privilege bypass vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-35168
Aliases: GHSA-c2r2-68p6-73xv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-26
Source: https://osv.dev/vulnerability/CVE-2023-35168
Type: osv

## Details
DataEase is an open source data visualization analysis tool to analyze data and gain insight into business trends. Affected versions of DataEase has a privilege bypass vulnerability where ordinary users can gain access to the user database. Exposed information includes md5 hashes of passwords, username, email, and phone number. The vulnerability has been fixed in v1.18.8. Users are advised to upgrade. There are no known workarounds for the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35168.json
- https://github.com/dataease/dataease/security/advisories/GHSA-c2r2-68p6-73xv
- https://nvd.nist.gov/vuln/detail/CVE-2023-35168
