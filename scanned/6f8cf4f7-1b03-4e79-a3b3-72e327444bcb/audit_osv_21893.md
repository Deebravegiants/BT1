# [M] Out-of-bounds read  in radareorg/radare2

## Summary
Severity: Medium
Advisory: CVE-2022-1207
CVSS: 6.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L)
Published: 2022-04-01
Source: https://osv.dev/vulnerability/CVE-2022-1207
Type: osv

## Details
Out-of-bounds read in GitHub repository radareorg/radare2 prior to 5.6.8. This vulnerability allows attackers to read sensitive information from outside the allocated buffer boundary.

## References
- https://huntr.dev/bounties/7b979e76-ae54-4132-b455-0833e45195eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1207.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1207
- https://github.com/radareorg/radare2/commit/605785b65dd356d46d4487faa41dbf90943b8bc1
