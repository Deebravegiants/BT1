# [M] CVE-2017-5462

## Summary
Severity: Medium
Advisory: CVE-2017-5462
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5462
Type: osv

## Details
A flaw in DRBG number generation within the Network Security Services (NSS) library where the internal state V does not correctly carry bits over. The NSS library has been updated to fix this issue to address this issue and Firefox ESR 52.1 has been updated with NSS version 3.28.4. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- https://security.gentoo.org/glsa/201705-04
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- http://www.securityfocus.com/bid/97940
- http://www.securitytracker.com/id/1038320
- https://www.debian.org/security/2017/dsa-3872
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1345089
