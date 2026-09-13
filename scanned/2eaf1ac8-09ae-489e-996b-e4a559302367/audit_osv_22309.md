# [C] Trivial signature forgery in ecdsautils

## Summary
Severity: Critical
Advisory: CVE-2022-24884
Aliases: GHSA-qhcg-9ffp-78pw
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2022-05-05
Source: https://osv.dev/vulnerability/CVE-2022-24884
Type: osv

## Details
ecdsautils is a tiny collection of programs used for ECDSA (keygen, sign, verify). `ecdsa_verify_[prepare_]legacy()` does not check whether the signature values `r` and `s` are non-zero. A signature consisting only of zeroes is always considered valid, making it trivial to forge signatures. Requiring multiple signatures from different public keys does not mitigate the issue: `ecdsa_verify_list_legacy()` will accept an arbitrary number of such forged signatures. Both the `ecdsautil verify` CLI command and the libecdsautil library are affected. The issue has been fixed in ecdsautils 0.4.1. All older versions of ecdsautils (including versions before the split into a library and a CLI utility) are vulnerable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24884.json
- https://github.com/freifunk-gluon/ecdsautils/security/advisories/GHSA-qhcg-9ffp-78pw
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4AKQH5WCBMJA3ODCSNERY6HVX4BX3ITG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G2JT57AAFIEL7JDO2ZBV25JKYME5NU54/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L7UBR3M4U3LA46BHXYSH7EN5GDG44GK7/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24884
- https://www.debian.org/security/2022/dsa-5132
- https://github.com/freifunk-gluon/ecdsautils/commit/1d4b091abdf15ad7b2312535b5b95ad70f6dbd08
- https://github.com/freifunk-gluon/ecdsautils/commit/39b6d0a77414fd41614953a0e185c4eefa2f88ad
- https://lists.debian.org/debian-lts-announce/2022/05/msg00007.html
