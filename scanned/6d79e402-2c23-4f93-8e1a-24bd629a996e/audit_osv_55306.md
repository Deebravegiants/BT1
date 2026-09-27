# [M] CVE-2025-2830

## Summary
Severity: Medium
Advisory: CVE-2025-2830
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-2830
Type: osv

## Details
By crafting a malformed file name for an attachment in a multipart message, an attacker can trick Thunderbird into including a directory listing of /tmp when the message is forwarded or edited as a new message. This vulnerability could allow attackers to disclose sensitive information from the victim's system. This vulnerability is not limited to Linux; similar behavior has been observed on Windows as well. This vulnerability affects Thunderbird < 137.0.2 and Thunderbird < 128.9.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-26/
- https://www.mozilla.org/security/advisories/mfsa2025-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1956379
