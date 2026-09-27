# [H] CVE-2023-43608

## Summary
Severity: High
Advisory: CVE-2023-43608
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-05
Source: https://osv.dev/vulnerability/CVE-2023-43608
Type: osv

## Details
A data integrity vulnerability exists in the BR_NO_CHECK_HASH_FOR functionality of Buildroot 2023.08.1 and dev commit 622698d7847. A specially crafted man-in-the-middle attack can lead to arbitrary command execution in the builder.

## References
- http://www.openwall.com/lists/oss-security/2023/12/11/1
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1845
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43608.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43608
