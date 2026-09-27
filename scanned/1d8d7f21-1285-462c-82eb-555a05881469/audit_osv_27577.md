# [C] CVE-2024-24002

## Summary
Severity: Critical
Advisory: CVE-2024-24002
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-24002
Type: osv

## Details
jshERP v3.3 is vulnerable to SQL Injection. The com.jsh.erp.controller.MaterialController: com.jsh.erp.utils.BaseResponseInfo getListWithStock() function of jshERP does not filter `column` and `order` parameters well enough, and an attacker can construct malicious payload to bypass jshERP's protection mechanism in `safeSqlParse` method for sql injection.

## References
- https://github.com/cxcxcxcxcxcxcxc/cxcxcxcxcxcxcxc/blob/main/cxcxcxcxcxc/about-2024/24002.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24002.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24002
- https://github.com/jishenghua/jshERP/issues/99
