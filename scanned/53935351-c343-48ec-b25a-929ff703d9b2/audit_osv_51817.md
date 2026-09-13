# [H] CVE-2021-41055

## Summary
Severity: High
Advisory: CVE-2021-41055
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-41055
Type: osv

## Details
Gajim 1.2.x and 1.3.x before 1.3.3 allows remote attackers to cause a denial of service (crash) via a crafted XMPP Last Message Correction (XEP-0308) message in multi-user chat, where the message ID equals the correction ID.

## References
- https://dev.gajim.org/gajim/gajim/-/tags/gajim-1.3.3
- https://dev.gajim.org/gajim/gajim/-/issues/10638
