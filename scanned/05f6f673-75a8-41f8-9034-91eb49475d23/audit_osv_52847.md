# [M] CVE-2022-1834

## Summary
Severity: Medium
Advisory: CVE-2022-1834
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1834
Type: osv

## Details
When displaying the sender of an email, and the sender name contained the Braille Pattern Blank space character multiple times, Thunderbird would have displayed all the spaces. This could have been used by an attacker to send an email message with the attacker's digital signature, that was shown with an arbitrary sender email address chosen by the attacker. If the sender name started with a false email address, followed by many Braille space characters, the attacker's email address was not visible. Because Thunderbird compared the invisible sender address with the signature's email address, if the signing key or certificate was accepted by Thunderbird, the email was shown as having a valid digital signature. This vulnerability affects Thunderbird < 91.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1767816
