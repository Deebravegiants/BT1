# [H] CVE-2020-6822

## Summary
Severity: High
Advisory: CVE-2020-6822
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-6822
Type: osv

## Details
On 32-bit builds, an out of bounds write could have occurred when processing an image larger than 4 GB in <code>GMPDecodeData</code>. It is possible that with enough effort this could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 68.7.0, Firefox ESR < 68.7, and Firefox < 75.

## References
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-12/
- https://www.mozilla.org/security/advisories/mfsa2020-13/
- https://www.mozilla.org/security/advisories/mfsa2020-14/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1544181
