# [H] CVE-2017-14500

## Summary
Severity: High
Advisory: CVE-2017-14500
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14500
Type: osv

## Details
Improper Neutralization of Special Elements used in an OS Command in the podcast playback function of Podbeuter in Newsbeuter 0.3 through 2.9 allows remote attackers to perform user-assisted code execution by crafting an RSS item with a media enclosure (i.e., a podcast file) that includes shell metacharacters in its filename, related to pb_controller.cpp and queueloader.cpp, a different vulnerability than CVE-2017-12904.

## References
- https://usn.ubuntu.com/4585-1/
- http://openwall.com/lists/oss-security/2017/09/16/1
- http://www.debian.org/security/2017/dsa-3977
- https://github.com/akrennmair/newsbeuter/issues/598
- https://github.com/akrennmair/newsbeuter/commit/26f5a4350f3ab5507bb8727051c87bb04660f333
- https://github.com/akrennmair/newsbeuter/commit/c8fea2f60c18ed30bdd1bb6f798e994e51a58260
