# [M] Insufficient randomness in generation of DNS query IDs in c-ares

## Summary
Severity: Medium
Advisory: CVE-2023-31147
Aliases: GHSA-8r8p-23f3-64c2
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-31147
Type: osv

## Details
c-ares is an asynchronous resolver library. When /dev/urandom or RtlGenRandom() are unavailable, c-ares uses rand() to generate random numbers used for DNS query ids. This is not a CSPRNG, and it is also not seeded by srand() so will generate predictable output. Input from the random number generator is fed into a non-compilant RC4 implementation and may not be as strong as the original RC4 implementation. No attempt is made to look for modern OS-provided CSPRNGs like arc4random() that is widely available. This issue has been fixed in version 1.19.1.

## References
- https://github.com/c-ares/c-ares/releases/tag/cares-1_19_1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Z5XFNXTNPTCBBVXFDNZQVLLIE6VRBY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBFWILTA33LOSV23P44FGTQQIDRJHIY7/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31147.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-8r8p-23f3-64c2
- https://nvd.nist.gov/vuln/detail/CVE-2023-31147
- https://security.gentoo.org/glsa/202310-09
