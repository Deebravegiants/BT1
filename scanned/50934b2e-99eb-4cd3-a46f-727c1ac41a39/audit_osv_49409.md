# [M] CVE-2019-11738

## Summary
Severity: Medium
Advisory: CVE-2019-11738
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11738
Type: osv

## Details
If a Content Security Policy (CSP) directive is defined that uses a hash-based source that takes the empty string as input, execution of any javascript: URIs will be allowed. This could allow for malicious JavaScript content to be run, bypassing CSP permissions. This vulnerability affects Firefox < 69 and Firefox ESR < 68.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1452037
