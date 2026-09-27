# [M] CVE-2019-9970

## Summary
Severity: Medium
Advisory: CVE-2019-9970
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-03-24
Source: https://osv.dev/vulnerability/CVE-2019-9970
Type: osv

## Details
Open Whisper Signal (aka Signal-Desktop) through 1.23.1 and the Signal Private Messenger application through 4.35.3 for Android are vulnerable to an IDN homograph attack when displaying messages containing URLs. This occurs because the application produces a clickable link even if (for example) Latin and Cyrillic characters exist in the same domain name, and the available font has an identical representation of characters from different alphabets.

## References
- http://www.securityfocus.com/bid/107550
- https://github.com/blazeinfosec/advisories/blob/master/signal-advisory.txt
