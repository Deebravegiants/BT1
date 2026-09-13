# [M] CVE-2023-50761

## Summary
Severity: Medium
Advisory: CVE-2023-50761
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-50761
Type: osv

## Details
The signature of a digitally signed S/MIME email message may optionally specify the signature creation date and time. If present, Thunderbird did not compare the signature creation date with the message date and time, and displayed a valid signature despite a date or time mismatch. This could be used to give recipients the impression that a message was sent at a different date or time. This vulnerability affects Thunderbird < 115.6.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://www.debian.org/security/2023/dsa-5582
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1865647
