# [H] CVE-2023-3417

## Summary
Severity: High
Advisory: CVE-2023-3417
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3417
Type: osv

## Details
Thunderbird allowed the Text Direction Override Unicode Character in filenames. An email attachment could be incorrectly shown as being a document file, while in  fact it was an executable file. Newer versions of Thunderbird will strip the character and show the correct file extension. This vulnerability affects Thunderbird < 115.0.1 and Thunderbird < 102.13.1.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00032.html
- https://www.debian.org/security/2023/dsa-5463
- https://www.mozilla.org/security/advisories/mfsa2023-27/
- https://www.mozilla.org/security/advisories/mfsa2023-28/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1835582
