# [M] CVE-2020-15652

## Summary
Severity: Medium
Advisory: CVE-2020-15652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-08-10
Source: https://osv.dev/vulnerability/CVE-2020-15652
Type: osv

## Details
By observing the stack trace for JavaScript errors in web workers, it was possible to leak the result of a cross-origin redirect. This applied only to content that can be parsed as script. This vulnerability affects Firefox < 79, Firefox ESR < 68.11, Firefox ESR < 78.1, Thunderbird < 68.11, and Thunderbird < 78.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00025.html
- https://usn.ubuntu.com/4443-1/
- https://www.mozilla.org/security/advisories/mfsa2020-30/
- https://www.mozilla.org/security/advisories/mfsa2020-35/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2020-31/
- https://www.mozilla.org/security/advisories/mfsa2020-32/
- https://www.mozilla.org/security/advisories/mfsa2020-33/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1634872
