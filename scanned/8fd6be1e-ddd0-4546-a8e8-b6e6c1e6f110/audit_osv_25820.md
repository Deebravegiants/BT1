# [M] CVE-2023-45229

## Summary
Severity: Medium
Advisory: CVE-2023-45229
Aliases: CVE-2023-45230, CVE-2023-45231, CVE-2023-45232, CVE-2023-45233, CVE-2023-45234, CVE-2023-45235, CVE-2023-45236, CVE-2023-45237
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/CVE-2023-45229
Type: osv

## Details
EDK2's Network Package is susceptible to an out-of-bounds read
 vulnerability when processing the IA_NA or IA_TA option in a DHCPv6 Advertise message. This
 vulnerability can be exploited by an attacker to gain unauthorized 
access and potentially lead to a loss of Confidentiality.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://www.kb.cert.org/vuls/id/132380
- http://packetstormsecurity.com/files/176574/PixieFail-Proof-Of-Concepts.html
- http://www.openwall.com/lists/oss-security/2024/01/16/2
- https://github.com/tianocore/edk2/security/advisories/GHSA-hc6x-cw6p-gj7h
- https://security.netapp.com/advisory/ntap-20240307-0011/
