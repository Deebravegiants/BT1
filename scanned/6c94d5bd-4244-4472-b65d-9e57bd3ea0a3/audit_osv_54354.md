# [M] CVE-2023-5169

## Summary
Severity: Medium
Advisory: CVE-2023-5169
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-5169
Type: osv

## Details
A compromised content process could have provided malicious data in a `PathRecording` resulting in an out-of-bounds write, leading to a potentially exploitable crash in a privileged process. This vulnerability affects Firefox < 118, Firefox ESR < 115.3, and Thunderbird < 115.3.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00015.html
- https://www.debian.org/security/2023/dsa-5513
- https://www.mozilla.org/security/advisories/mfsa2023-41/
- https://www.mozilla.org/security/advisories/mfsa2023-42/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AY642Z6JZODQJE7Z62CFREVUHEGCXGPD/
- https://www.mozilla.org/security/advisories/mfsa2023-43/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1846685
- https://www.debian.org/security/2023/dsa-5506
- https://lists.debian.org/debian-lts-announce/2023/09/msg00034.html
