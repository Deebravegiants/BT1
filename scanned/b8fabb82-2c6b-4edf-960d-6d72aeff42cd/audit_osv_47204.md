# [M] CVE-2016-10376

## Summary
Severity: Medium
Advisory: CVE-2016-10376
CVSS: 4.5 (CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-05-28
Source: https://osv.dev/vulnerability/CVE-2016-10376
Type: osv

## Details
Gajim through 0.16.7 unconditionally implements the "XEP-0146: Remote Controlling Clients" extension. This can be abused by malicious XMPP servers to, for example, extract plaintext from OTR encrypted sessions.

## References
- https://security.gentoo.org/glsa/201707-14
- http://www.debian.org/security/2017/dsa-3943
- https://bugs.debian.org/863445
- https://mail.jabber.org/pipermail/standards/2016-August/031335.html
- https://dev.gajim.org/gajim/gajim/commit/cb65cfc5aed9efe05208ebbb7fb2d41fcf7253cc
- https://dev.gajim.org/gajim/gajim/issues/8378
