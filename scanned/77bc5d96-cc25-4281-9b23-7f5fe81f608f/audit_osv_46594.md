# [H] CVE-2014-0160

## Summary
Severity: High
Advisory: CVE-2014-0160
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2014-04-07
Source: https://osv.dev/vulnerability/CVE-2014-0160
Type: osv

## Details
The (1) TLS and (2) DTLS implementations in OpenSSL 1.0.1 before 1.0.1g do not properly handle Heartbeat Extension packets, which allows remote attackers to obtain sensitive information from process memory via crafted packets that trigger a buffer over-read, as demonstrated by reading private keys, related to d1_both.c and t1_lib.c, aka the Heartbleed bug.

## References
- http://advisories.mageia.org/MGASA-2014-0165.html
- http://blog.fox-it.com/2014/04/08/openssl-heartbleed-bug-live-blog/
- http://cogentdatahub.com/ReleaseNotes.html
- http://heartbleed.com/
- http://lists.fedoraproject.org/pipermail/package-announce/2014-April/131221.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-April/131291.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-August/136473.html
- http://lists.opensuse.org/opensuse-security-announce/2014-04/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2014-04/msg00005.html
- http://lists.opensuse.org/opensuse-updates/2014-04/msg00061.html
- http://marc.info/?l=bugtraq&m=139722163017074&w=2
- http://marc.info/?l=bugtraq&m=139757726426985&w=2
- http://marc.info/?l=bugtraq&m=139757819327350&w=2
- http://marc.info/?l=bugtraq&m=139757919027752&w=2
- http://marc.info/?l=bugtraq&m=139758572430452&w=2
- http://marc.info/?l=bugtraq&m=139765756720506&w=2
- http://marc.info/?l=bugtraq&m=139774054614965&w=2
- http://marc.info/?l=bugtraq&m=139774703817488&w=2
- http://marc.info/?l=bugtraq&m=139808058921905&w=2
- http://marc.info/?l=bugtraq&m=139817685517037&w=2
