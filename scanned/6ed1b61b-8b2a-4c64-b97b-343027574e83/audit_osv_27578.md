# [C] CVE-2024-24003

## Summary
Severity: Critical
Advisory: CVE-2024-24003
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-24003
Type: osv

## Details
jshERP v3.3 is vulnerable to SQL Injection. The com.jsh.erp.controller.DepotHeadController: com.jsh.erp.utils.BaseResponseInfo findInOutMaterialCount() function of jshERP does not filter `column` and `order` parameters well enough, and an attacker can construct malicious payload to bypass jshERP's protection mechanism in `safeSqlParse` method for sql injection.

## References
- https://github.com/cxcxcxcxcxcxcxc/cxcxcxcxcxcxcxc/blob/main/cxcxcxcxcxc/about-2024/24003.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24003.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24003
- https://github.com/jishenghua/jshERP/issues/99
