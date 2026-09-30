# [H] CVE-2021-43610

## Summary
Severity: High
Advisory: CVE-2021-43610
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-12
Source: https://osv.dev/vulnerability/CVE-2021-43610
Type: osv

## Details
Belledonne Belle-sip before 5.0.20 can crash applications such as Linphone via an invalid From header (request URI without a parameter) in an unauthenticated SIP message, a different issue than CVE-2021-33056.

## References
- https://github.com/BelledonneCommunications/belle-sip/commit/d3f0651531e45e91c2e60f3a16a8b612802e5d2d
- https://github.com/BelledonneCommunications/belle-sip/compare/5.0.18...5.0.20
