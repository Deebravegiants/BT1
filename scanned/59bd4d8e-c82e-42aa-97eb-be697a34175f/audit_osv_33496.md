# [H] CVE-2025-44040

## Summary
Severity: High
Advisory: CVE-2025-44040
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/CVE-2025-44040
Type: osv

## Details
An issue in OrangeHRM v.5.7 allows an attacker to escalate privileges via UserService.php and the checkForOldHash function. Authentication decisions may be made via PHP loose-equality comparisons if a specific MD5 value is present in the credential store. NOTE: this is disputed by the Supplier because an adversary has no way to place the specific MD5 value into the credential store (unless they already have full privileges) and because the specific MD5 value would not realistically be present otherwise.

## References
- https://github.com/orangehrm/orangehrm/releases/tag/v5.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/44xxx/CVE-2025-44040.json
- https://github.com/hexomedin3/advisories/tree/main/CVE-2025-44040
- https://nvd.nist.gov/vuln/detail/CVE-2025-44040
