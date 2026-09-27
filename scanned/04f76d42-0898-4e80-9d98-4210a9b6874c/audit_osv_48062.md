# [M] CVE-2017-17688

## Summary
Severity: Medium
Advisory: CVE-2017-17688
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2017-17688
Type: osv

## Details
The OpenPGP specification allows a Cipher Feedback Mode (CFB) malleability-gadget attack that can indirectly lead to plaintext exfiltration, aka EFAIL. NOTE: third parties report that this is a problem in applications that mishandle the Modification Detection Code (MDC) feature or accept an obsolete packet type, not a problem in the OpenPGP specification

## References
- http://flaked.sockpuppet.org/2018/05/16/a-unified-timeline.html
- http://www.securitytracker.com/id/1040904
- https://lists.gnupg.org/pipermail/gnupg-users/2018-May/060334.html
- https://twitter.com/matthew_d_green/status/995996706457243648
- https://www.synology.com/support/security/Synology_SA_18_22
- http://www.securityfocus.com/bid/104162
- https://news.ycombinator.com/item?id=17066419
- https://protonmail.com/blog/pgp-vulnerability-efail
- https://www.patreon.com/posts/cybersecurity-15-18814817
- https://efail.de
