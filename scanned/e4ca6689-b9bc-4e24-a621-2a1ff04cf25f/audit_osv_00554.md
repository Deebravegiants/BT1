# [M] ALPINE-CVE-2017-15705

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-15705
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15705
Type: osv

## Affected
- Alpine:v3.10: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.11: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.12: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.13: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.14: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.15: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.16: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.17: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.18: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.19: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.20: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.21: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.22: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.23: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.24: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.8: `spamassassin` — affected >=0 <3.4.3-r0
- Alpine:v3.9: `spamassassin` — affected >=0 <3.4.2-r0

## Details
A denial of service vulnerability was identified that exists in Apache SpamAssassin before 3.4.2. The vulnerability arises with certain unclosed tags in emails that cause markup to be handled incorrectly leading to scan timeouts. In Apache SpamAssassin, using HTML::Parser, we setup an object and hook into the begin and end tag event handlers In both cases, the "open" event is immediately followed by a "close" event - even if the tag *does not* close in the HTML being parsed. Because of this, we are missing the "text" event to deal with the object normally. This can cause carefully crafted emails that might take more scan time than expected leading to a Denial of Service. The issue is possibly a bug or design decision in HTML::Parser that specifically impacts the way Apache SpamAssassin uses the module with poorly formed html. The exploit has been seen in the wild but not believed to have been purposefully part of a Denial of Service attempt. We are concerned that there may be attempts to abuse the vulnerability in the future.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15705
