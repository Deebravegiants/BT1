# [H] CVE-2022-40274

## Summary
Severity: High
Advisory: CVE-2022-40274
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-30
Source: https://osv.dev/vulnerability/CVE-2022-40274
Type: osv

## Details
Gridea version 0.9.3 allows an external attacker to execute arbitrary code remotely on any client attempting to view a malicious markdown file through Gridea. This is possible because the application has the 'nodeIntegration' option enabled.

## References
- https://fluidattacks.com/advisories/marshmello/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40274.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40274
- https://github.com/getgridea/gridea
