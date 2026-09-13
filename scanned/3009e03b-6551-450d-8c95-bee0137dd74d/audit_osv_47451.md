# [H] CVE-2016-5284

## Summary
Severity: High
Advisory: CVE-2016-5284
CVSS: 7.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2016-09-22
Source: https://osv.dev/vulnerability/CVE-2016-5284
Type: osv

## Details
Mozilla Firefox before 49.0, Firefox ESR 45.x before 45.4, and Thunderbird < 45.4 rely on unintended expiration dates for Preloaded Public Key Pinning, which allows man-in-the-middle attackers to spoof add-on updates by leveraging possession of an X.509 server certificate for addons.mozilla.org signed by an arbitrary built-in Certification Authority.

## References
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.securitytracker.com/id/1036852
- http://www.securityfocus.com/bid/93049
- http://rhn.redhat.com/errata/RHSA-2016-1912.html
- http://seclists.org/dailydave/2016/q3/51
- http://www.debian.org/security/2016/dsa-3674
- http://www.mozilla.org/security/announce/2016/mfsa2016-85.html
- https://blog.mozilla.org/security/2016/09/16/update-on-add-on-pinning-vulnerability/
- https://security.gentoo.org/glsa/201701-15
- https://www.mozilla.org/security/advisories/mfsa2016-86/
- https://www.mozilla.org/security/advisories/mfsa2016-88/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1303127
- https://hackernoon.com/tor-browser-exposed-anti-privacy-implantation-at-mass-scale-bd68e9eb1e95
