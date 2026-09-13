# [M] CVE-2020-10769

## Summary
Severity: Medium
Advisory: CVE-2020-10769
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-26
Source: https://osv.dev/vulnerability/CVE-2020-10769
Type: osv

## Details
A buffer over-read flaw was found in RH kernel versions before 5.0 in crypto_authenc_extractkeys in crypto/authenc.c in the IPsec Cryptographic algorithm's module, authenc. When a payload longer than 4 bytes, and is not following 4-byte alignment boundary guidelines, it causes a buffer over-read threat, leading to a system crash. This flaw allows a local attacker with user privileges to cause a denial of service.

## References
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1708775%3B
- https://lkml.org/lkml/2019/1/21/675
