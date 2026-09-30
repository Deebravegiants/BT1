# [M] CVE-2020-1771

## Summary
Severity: Medium
Advisory: CVE-2020-1771
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-03-27
Source: https://osv.dev/vulnerability/CVE-2020-1771
Type: osv

## Details
Attacker is able craft an article with a link to the customer address book with malicious content (JavaScript). When agent opens the link, JavaScript code is executed due to the missing parameter encoding. This issue affects: ((OTRS)) Community Edition: 6.0.26 and prior versions. OTRS: 7.0.15 and prior versions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00066.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00077.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://otrs.com/release-notes/otrs-security-advisory-2020-08/
