# [M] CVE-2019-11762

## Summary
Severity: Medium
Advisory: CVE-2019-11762
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-11762
Type: osv

## Details
If two same-origin documents set document.domain differently to become cross-origin, it was possible for them to call arbitrary DOM methods/getters/setters on the now-cross-origin window. This vulnerability affects Firefox < 70, Thunderbird < 68.2, and Firefox ESR < 68.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-33/
- https://www.mozilla.org/security/advisories/mfsa2019-34/
- https://www.mozilla.org/security/advisories/mfsa2019-35/
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4335-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1582857
