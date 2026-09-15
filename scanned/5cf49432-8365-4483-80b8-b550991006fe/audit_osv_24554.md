# [H] CVE-2023-22792

## Summary
Severity: High
Advisory: CVE-2023-22792
Aliases: GHSA-p84v-45xj-wwqj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-09
Source: https://osv.dev/vulnerability/CVE-2023-22792
Type: osv

## Details
A regular expression based DoS vulnerability in Action Dispatch <6.0.6.1,< 6.1.7.1, and <7.0.4.1. Specially crafted cookies, in combination with a specially crafted X_FORWARDED_HOST header can cause the regular expression engine to enter a state of catastrophic backtracking. This can cause the process to use large amounts of CPU and memory, leading to a possible DoS vulnerability All users running an affected release should either upgrade or use one of the workarounds immediately.

## References
- https://discuss.rubyonrails.org/t/cve-2023-22792-possible-redos-based-dos-vulnerability-in-action-dispatch/82115
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22792.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22792
- https://security.netapp.com/advisory/ntap-20240202-0007/
- https://www.debian.org/security/2023/dsa-5372
