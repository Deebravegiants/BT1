# [M] CVE-2015-3182

## Summary
Severity: Medium
Advisory: CVE-2015-3182
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-3182
Type: osv

## Details
epan/dissectors/packet-dec-dnart.c in the DECnet NSP/RT dissector in Wireshark 1.10.12 through 1.10.14 mishandles a certain strdup return value, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- https://security.gentoo.org/glsa/201510-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1219409
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/74586
- http://www.securitytracker.com/id/1032279
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=373deb5f4182a5c4ab8c8418a7bbaa5d6e72bb05
