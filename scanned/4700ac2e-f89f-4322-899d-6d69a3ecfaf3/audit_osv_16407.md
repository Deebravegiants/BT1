# [H] CVE-2019-6486

## Summary
Severity: High
Advisory: CVE-2019-6486
Aliases: GO-2022-0217
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-01-24
Source: https://osv.dev/vulnerability/CVE-2019-6486
Type: osv

## Details
Go before 1.10.8 and 1.11.x before 1.11.5 mishandles P-521 and P-384 elliptic curves, which allows attackers to cause a denial of service (CPU consumption) or possibly conduct ECDH private key recovery attacks.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00015.html
- https://groups.google.com/forum/#%21topic/golang-announce/mVeX35iXuSw
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00042.html
- http://www.securityfocus.com/bid/106740
- https://github.com/golang/go/issues/29903
- https://github.com/google/wycheproof
- https://lists.debian.org/debian-lts-announce/2019/02/msg00009.html
- https://www.debian.org/security/2019/dsa-4379
- https://www.debian.org/security/2019/dsa-4380
- https://github.com/golang/go/commit/42b42f71cf8f5956c09e66230293dfb5db652360
