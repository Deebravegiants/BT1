# [H] CVE-2020-6807

## Summary
Severity: High
Advisory: CVE-2020-6807
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-6807
Type: osv

## Details
When a device was changed while a stream was about to be destroyed, the <code>stream-reinit</code> task may have been executed after the stream was destroyed, causing a use-after-free and a potentially exploitable crash. This vulnerability affects Thunderbird < 68.6, Firefox < 74, Firefox < ESR68.6, and Firefox ESR < 68.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-10/
- https://usn.ubuntu.com/4328-1/
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-08/
- https://www.mozilla.org/security/advisories/mfsa2020-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1614971
