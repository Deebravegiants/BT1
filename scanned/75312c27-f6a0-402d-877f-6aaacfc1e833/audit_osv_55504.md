# [M] CVE-2025-5986

## Summary
Severity: Medium
Advisory: CVE-2025-5986
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2025-5986
Type: osv

## Details
A crafted HTML email using mailbox:/// links can trigger automatic, unsolicited downloads of .pdf files to the user's desktop or home directory without prompting, even if auto-saving is disabled. This behavior can be abused to fill the disk with garbage data (e.g. using /dev/urandom on Linux) or to leak Windows credentials via SMB links when the email is viewed in HTML mode. While user interaction is required to download the .pdf file, visual obfuscation can conceal the download trigger. Viewing the email in HTML mode is enough to load external content. This vulnerability affects Thunderbird < 128.11.1 and Thunderbird < 139.0.2.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00002.html
- https://www.mozilla.org/security/advisories/mfsa2025-49/
- https://www.mozilla.org/security/advisories/mfsa2025-50/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1958580%2C1968012
