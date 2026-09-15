# [M] CVE-2019-11748

## Summary
Severity: Medium
Advisory: CVE-2019-11748
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11748
Type: osv

## Details
WebRTC in Firefox will honor persisted permissions given to sites for access to microphone and camera resources even when in a third-party context. In light of recent high profile vulnerabilities in other software, a decision was made to no longer persist these permissions. This avoids the possibility of trusted WebRTC resources being invisibly embedded in web content and abusing permissions previously given by users. Users will now be prompted for permissions on each use. This vulnerability affects Firefox < 69 and Firefox ESR < 68.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00017.html
- https://www.mozilla.org/security/advisories/mfsa2019-25/
- https://www.mozilla.org/security/advisories/mfsa2019-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1564588
