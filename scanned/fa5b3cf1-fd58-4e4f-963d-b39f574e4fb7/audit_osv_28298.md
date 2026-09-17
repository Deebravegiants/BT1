# [H] Xorg-x11-server: heap buffer overread/data leakage in procxipassivegrabdevice

## Summary
Severity: High
Advisory: CVE-2024-31081
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-31081
Type: osv

## Details
A heap-based buffer over-read vulnerability was found in the X.org server's ProcXIPassiveGrabDevice() function. This issue occurs when byte-swapped length values are used in replies, potentially leading to memory leakage and segmentation faults, particularly when triggered by a client with a different endianness. This vulnerability could be exploited by an attacker to cause the X server to read heap memory values and then transmit them back to the client until encountering an unmapped page, resulting in a crash. Despite the attacker's inability to control the specific memory copied into the replies, the small length values typically stored in a 32-bit integer can result in significant attempted out-of-bounds reads.

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
