# [M] Consul-template is vulnerable to path redirection in writeToFile through symlink attack

## Summary
Severity: Medium
Advisory: CVE-2026-14361
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14361
Type: osv

## Details
The consul-template library before version 0.42.1 is vulnerable to a path redirection issue in the writeToFile template helper that may allow template output to be written outside the intended directory or to overwrite an existing file. This vulnerability (CVE-2026-14361) is fixed in consul-template 0.42.1.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-20-consul-template-vulnerable-to-path-redirections-in-writetofile/77559
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14361.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14361
- https://github.com/hashicorp/consul-template
