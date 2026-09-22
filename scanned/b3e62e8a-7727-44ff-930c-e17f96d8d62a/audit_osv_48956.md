# [C] CVE-2018-18512

## Summary
Severity: Critical
Advisory: CVE-2018-18512
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2018-18512
Type: osv

## Details
A use-after-free vulnerability can occur while playing a sound notification in Thunderbird. The memory storing the sound data is immediately freed, although the sound is still being played asynchronously, leading to a potentially exploitable crash. This vulnerability affects Thunderbird < 60.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1482659
