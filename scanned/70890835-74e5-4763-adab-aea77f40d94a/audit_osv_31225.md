# [M] MongoDB C Driver bson_strfreev may be susceptible to integer overflow

## Summary
Severity: Medium
Advisory: CVE-2024-6381
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-07-02
Source: https://osv.dev/vulnerability/CVE-2024-6381
Type: osv

## Details
The bson_strfreev function in the MongoDB C driver library may be susceptible to an integer overflow where the function will try to free memory at a negative offset. This may result in memory corruption. This issue affected libbson versions prior to 1.26.2

## References
- https://jira.mongodb.org/browse/CDRIVER-5622
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00027.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6381.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6381
