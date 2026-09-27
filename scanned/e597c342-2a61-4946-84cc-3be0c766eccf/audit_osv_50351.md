# [M] CVE-2020-13132

## Summary
Severity: Medium
Advisory: CVE-2020-13132
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-13132
Type: osv

## Details
An issue was discovered in Yubico libykpiv before 2.1.0. An attacker can trigger an incorrect free() in the ykpiv_util_generate_key() function in lib/util.c through incorrect error handling code. This could be used to cause a denial of service attack.

## References
- https://www.yubico.com/support/security-advisories/ysa-2020-02/
- https://blog.inhq.net/posts/yubico-libykpiv-vuln/
