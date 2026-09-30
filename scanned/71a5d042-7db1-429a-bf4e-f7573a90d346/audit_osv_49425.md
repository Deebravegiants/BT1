# [M] CVE-2019-11761

## Summary
Severity: Medium
Advisory: CVE-2019-11761
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-11761
Type: osv

## Details
By using a form with a data URI it was possible to gain access to the privileged JSONView object that had been cloned into content. Impact from exposing this object appears to be minimal, however it was a bypass of existing defense in depth mechanisms. This vulnerability affects Firefox < 70, Thunderbird < 68.2, and Firefox ESR < 68.2.

## References
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2019-33/
- https://www.mozilla.org/security/advisories/mfsa2019-34/
- https://www.mozilla.org/security/advisories/mfsa2019-35/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1561502
