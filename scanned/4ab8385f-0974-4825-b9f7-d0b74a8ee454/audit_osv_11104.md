# [M] CVE-2017-6076

## Summary
Severity: Medium
Advisory: CVE-2017-6076
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-6076
Type: osv

## Details
In versions of wolfSSL before 3.10.2 the function fp_mul_comba makes it easier to extract RSA key information for a malicious user who has access to view cache on a machine.

## References
- http://www.securityfocus.com/bid/96422
- https://github.com/wolfSSL/wolfssl/releases/tag/v3.10.2-stable
