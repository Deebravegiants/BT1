# [C] CVE-2023-28753

## Summary
Severity: Critical
Advisory: CVE-2023-28753
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-28753
Type: osv

## Details
netconsd prior to v0.2 was vulnerable to an integer overflow in its parse_packet function. A malicious individual could leverage this overflow to create heap memory corruption with attacker controlled data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28753.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28753
- https://www.facebook.com/security/advisories/cve-2023-28753
- https://github.com/facebook/netconsd/commit/9fc54edf54f7caea1189c2b979337ed37af2c60e
