# [M] Linux-PAM pam_userdb Observable Timing Discrepancy in Plaintext Password Comparison

## Summary
Severity: Medium
Advisory: CVE-2026-54411
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P/AU:N/V:D)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/CVE-2026-54411
Type: osv

## Details
Linux-PAM through 1.7.2 contains an observable timing discrepancy (CWE-208) in the pam_userdb module's plaintext-password comparison path in modules/pam_userdb/pam_userdb.c that allows a local or network-adjacent attacker able to repeatedly drive authentication through a calling service to recover the plaintext password of a target account by measuring response-timing differences.

## References
- https://github.com/linux-pam/linux-pam/blob/master/libpam/include/pam_inline.h
- https://github.com/linux-pam/linux-pam/blob/master/modules/pam_userdb/pam_userdb.c#L327
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54411.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54411
- https://github.com/linux-pam/linux-pam
- https://cwe.mitre.org/data/definitions/208.html
