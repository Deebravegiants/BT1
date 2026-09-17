# [M] CVE-2023-50762

## Summary
Severity: Medium
Advisory: CVE-2023-50762
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-50762
Type: osv

## Details
When processing a PGP/MIME payload that contains digitally signed text, the first paragraph of the text was never shown to the user. This is because the text was interpreted as a MIME message and the first paragraph was always treated as an email header section. A digitally signed text from a different context, such as a signed GIT commit, could be used to spoof an email message. This vulnerability affects Thunderbird < 115.6.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://www.debian.org/security/2023/dsa-5582
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1862625
