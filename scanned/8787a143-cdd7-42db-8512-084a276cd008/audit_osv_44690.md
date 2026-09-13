# [M] SiYuan through 3.8.1 Authorization Bypass via getFile

## Summary
Severity: Medium
Advisory: CVE-2026-85578
Aliases: GHSA-8ggq-wq3f-vxrw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85578
Type: osv

## Details
SiYuan through 3.8.1 contains an authorization bypass vulnerability in the /api/file/getFile endpoint that allows readers to retrieve files from notebooks explicitly configured as Visible:false. Attackers with reader role can access private workspace files including notebook metadata and internal configuration by knowing the hidden notebook identifier and file path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85578.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-8ggq-wq3f-vxrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-85578
- https://www.vulncheck.com/advisories/siyuan-through-3.8.1-authorization-bypass-via-getfile
