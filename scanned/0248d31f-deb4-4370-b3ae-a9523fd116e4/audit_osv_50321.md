# [M] CVE-2020-12402

## Summary
Severity: Medium
Advisory: CVE-2020-12402
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12402
Type: osv

## Details
During RSA key generation, bignum implementations used a variation of the Binary Extended Euclidean Algorithm which entailed significantly input-dependent flow. This allowed an attacker able to perform electromagnetic-based side channel attacks to record traces leading to the recovery of the secret primes. *Note:* An unmodified Firefox browser does not generate RSA keys in normal operation and is not affected, but products built on top of it might. This vulnerability affects Firefox < 78.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UWVDJRARXNWWWTCGMM63EXLQHH2LNOXO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RFL6UNFK4MG2WDXLMLFAEIUSM5EUK7CG/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00029.html
- https://usn.ubuntu.com/4417-1/
- https://usn.ubuntu.com/4417-2/
- https://www.debian.org/security/2020/dsa-4726
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00027.html
- https://security.gentoo.org/glsa/202007-10
- https://www.mozilla.org/security/advisories/mfsa2020-24/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00049.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631597
