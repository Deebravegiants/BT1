# [H] CVE-2018-16151

## Summary
Severity: High
Advisory: CVE-2018-16151
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-26
Source: https://osv.dev/vulnerability/CVE-2018-16151
Type: osv

## Details
In verify_emsa_pkcs1_signature() in gmp_rsa_public_key.c in the gmp plugin in strongSwan 4.x and 5.x before 5.7.0, the RSA implementation based on GMP does not reject excess data after the encoded algorithm OID during PKCS#1 v1.5 signature verification. Similar to the flaw in the same version of strongSwan regarding digestAlgorithm.parameters, a remote attacker can forge signatures when small public exponents are being used, which could lead to impersonation when only an RSA signature is used for IKEv2 authentication.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00047.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00032.html
- https://security.gentoo.org/glsa/201811-16
- https://usn.ubuntu.com/3771-1/
- https://www.debian.org/security/2018/dsa-4305
- https://www.strongswan.org/blog/2018/09/24/strongswan-vulnerability-%28cve-2018-16151%2C-cve-2018-16152%29.html
