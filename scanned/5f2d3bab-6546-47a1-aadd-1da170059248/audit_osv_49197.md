# [M] CVE-2018-5389

## Summary
Severity: Medium
Advisory: CVE-2018-5389
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-5389
Type: osv

## Details
The Internet Key Exchange v1 main mode is vulnerable to offline dictionary or brute force attacks. Reusing a key pair across different versions and modes of IKE could lead to cross-protocol authentication bypasses. It is well known, that the aggressive mode of IKEv1 PSK is vulnerable to offline dictionary or brute force attacks. For the main mode, however, only an online attack against PSK authentication was thought to be feasible. This vulnerability could allow an attacker to recover a weak Pre-Shared Key or enable the impersonation of a victim host or network.

## References
- https://my.f5.com/manage/s/article/K42378447
- https://blogs.cisco.com/security/great-cipher-but-where-did-you-get-that-key
- https://www.kb.cert.org/vuls/id/857035
- https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-felsch.pdf
- https://web-in-security.blogspot.com/2018/08/practical-dictionary-attack-on-ipsec-ike.html
