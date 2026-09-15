# [H] CVE-2024-1936

## Summary
Severity: High
Advisory: CVE-2024-1936
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2024-1936
Type: osv

## Details
The encrypted subject of an email message could be incorrectly and permanently assigned to an arbitrary other email message in Thunderbird's local cache. Consequently, when replying to the contaminated email message, the user might accidentally leak the confidential subject to a third-party. While this update fixes the bug and avoids future message contamination, it does not automatically repair existing contaminations. Users are advised to use the repair folder functionality, which is available from the context menu of email folders, which will erase incorrect subject assignments. This vulnerability affects Thunderbird < 115.8.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1860977
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
