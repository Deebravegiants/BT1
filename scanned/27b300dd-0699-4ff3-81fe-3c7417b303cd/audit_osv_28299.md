# [H] Xorg-x11-server: use-after-free in procrenderaddglyphs

## Summary
Severity: High
Advisory: CVE-2024-31083
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-31083
Type: osv

## Details
A use-after-free vulnerability was found in the ProcRenderAddGlyphs() function of Xorg servers. This issue occurs when AllocateGlyph() is called to store new glyphs sent by the client to the X server, potentially resulting in multiple entries pointing to the same non-refcounted glyphs. Consequently, ProcRenderAddGlyphs() may free a glyph, leading to a use-after-free scenario when the same glyph pointer is subsequently accessed. This flaw allows an authenticated attacker to execute arbitrary code on the system by sending a specially crafted request.

## References
- http://www.openwall.com/lists/oss-security/2024/04/03/13
- http://www.openwall.com/lists/oss-security/2024/04/12/10
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6TF7FZXOKHIKPZXYIMSQXKVH7WITKV3V/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EBLQJIAXEDMEGRGZMSH7CWUJHSVKUWLV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/P73U4DAAWLFZAPD75GLXTGMSTTQWW5AP/
- https://access.redhat.com/errata/RHSA-2024:1785
- https://access.redhat.com/errata/RHSA-2024:2036
- https://access.redhat.com/errata/RHSA-2024:2037
- https://access.redhat.com/errata/RHSA-2024:2038
- https://access.redhat.com/errata/RHSA-2024:2039
- https://access.redhat.com/errata/RHSA-2024:2040
- https://access.redhat.com/errata/RHSA-2024:2041
- https://access.redhat.com/errata/RHSA-2024:2042
- https://access.redhat.com/errata/RHSA-2024:2080
- https://access.redhat.com/errata/RHSA-2024:2616
- https://access.redhat.com/errata/RHSA-2024:3258
- https://access.redhat.com/errata/RHSA-2024:3261
- https://access.redhat.com/errata/RHSA-2024:3343
