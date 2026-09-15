# [H] CVE-2022-45412

## Summary
Severity: High
Advisory: CVE-2022-45412
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45412
Type: osv

## Details
When resolving a symlink such as <code>file:///proc/self/fd/1</code>, an error message may be produced where the symlink was resolved to a string containing unitialized memory in the buffer. <br>*This bug only affects Thunderbird on Unix-based operated systems (Android, Linux, MacOS). Windows is unaffected.*. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1791029
