# [H] phpseclib guardrails needed on OID length

## Summary
Severity: High
Advisory: GHSA-f2qx-66wf-wvvx
CVE: CVE-2024-27355
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-f2qx-66wf-wvvx
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.47
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.36
- Packagist: `phpseclib/phpseclib` — affected >=0.1.1 <1.0.23

## Details
### Impact
Any application using that loads untrusted ASN1 files (eg. X509 certificates, RSA PKCS8 private or public keys, etc).

### Patches
https://github.com/phpseclib/phpseclib/commit/e32531001b4d62c66c3d824ccef54ffad835eb59

### Workarounds
No.

### Resources
https://github.com/phpseclib/phpseclib/commit/e32531001b4d62c66c3d824ccef54ffad835eb59
https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-599-shi-bing.pdf

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-f2qx-66wf-wvvx
- https://nvd.nist.gov/vuln/detail/CVE-2024-27355
- https://github.com/phpseclib/phpseclib/commit/e32531001b4d62c66c3d824ccef54ffad835eb59
- https://gist.github.com/katzj/ee72f3c2a00590812b2ea3c0c8890e0b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpseclib/phpseclib/CVE-2024-27355.yaml
- https://github.com/phpseclib/phpseclib
- https://github.com/phpseclib/phpseclib/blob/978d081fe50ff92879c50ff143c62a143edb0117/phpseclib/File/ASN1.php#L1129
- https://lists.debian.org/debian-lts-announce/2024/03/msg00002.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00003.html
