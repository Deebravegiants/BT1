# [C] Use-After-Free in str_escape in mruby/mruby in mruby/mruby

## Summary
Severity: Critical
Advisory: CVE-2022-1212
CVSS: 9.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2022-1212
Type: osv

## Details
Use-After-Free in str_escape in mruby/mruby in GitHub repository mruby/mruby prior to 3.2. Possible arbitrary code execution if being exploited.

## References
- https://huntr.dev/bounties/9fcc06d0-08e4-49c8-afda-2cae40946abe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1212.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1212
- https://github.com/mruby/mruby/commit/3cf291f72224715942beaf8553e42ba8891ab3c6
