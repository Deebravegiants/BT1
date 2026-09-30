# [M] CVE-2016-8871

## Summary
Severity: Medium
Advisory: CVE-2016-8871
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8871
Type: osv

## Details
In Botan 1.11.29 through 1.11.32, RSA decryption with certain padding options had a detectable timing channel which could given sufficient queries be used to recover plaintext, aka an "OAEP side channel" attack.

## References
- http://www.securityfocus.com/bid/94225
- https://botan.randombit.net/security.html
