# [C] CVE-2025-51742

## Summary
Severity: Critical
Advisory: CVE-2025-51742
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-51742
Type: osv

## Details
An issue was discovered in jishenghua JSH_ERP 2.3.1. The /material/getMaterialEnableSerialNumberList endpoint passes the search query parameter directly to parseObject(), introducing a Fastjson deserialization vulnerability that can lead to RCE via JDBC payloads.

## References
- https://gist.github.com/Paxsizy/a40334ffa7f05c42bf0348833f830108
- https://gitee.com/jishenghua
- https://gitee.com/jishenghua/JSH_ERP
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51742.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51742
- https://blog.hackpax.top/jsh-erp/
