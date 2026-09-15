# [M] CVE-2026-0818

## Summary
Severity: Medium
Advisory: CVE-2026-0818
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-0818
Type: osv

## Details
When a user explicitly requested Thunderbird to decrypt an inline OpenPGP message that was embedded in a text section of an email that was formatted and styled with HTML and CSS, then the decrypted contents were rendered in a context in which the CSS styles from the outer messages were active. If the user had additionally allowed loading of the remote content referenced by the outer email message, and the email was crafted by the sender using a combination of CSS rules and fonts and animations, then it was possible to extract the secret contents of the email. This vulnerability affects Thunderbird < 147.0.1 and Thunderbird < 140.7.1.

## References
- https://lists.debian.org/debian-lts-announce/2026/02/msg00005.html
- https://www.mozilla.org/security/advisories/mfsa2026-08/
- https://www.mozilla.org/security/advisories/mfsa2026-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1881530
