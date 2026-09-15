# [M] batman-adv: Avoid infinite loop trying to resize local TT

## Summary
Severity: Medium
Advisory: CVE-2024-35982
Ecosystem: Linux
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35982
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.156, >=5.16.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: Avoid infinite loop trying to resize local TT

If the MTU of one of an attached interface becomes too small to transmit
the local translation table then it must be resized to fit inside all
fragments (when enabled) or a single packet.

But if the MTU becomes too low to transmit even the header + the VLAN
specific part then the resizing of the local TT will never succeed. This
can for example happen when the usable space is 110 bytes and 11 VLANs are
on top of batman-adv. In this case, at least 116 byte would be needed.
There will just be an endless spam of

   batman_adv: batadv0: Forced to purge local tt entries to fit new maximum fragment MTU (110)

in the log but the function will never finish. Problem here is that the
timeout will be halved all the time and will then stagnate at 0 and
therefore never be able to reduce the table even more.

There are other scenarios possible with a similar result. The number of
BATADV_TT_CLIENT_NOPURGE entries in the local TT can for example be too
high to fit inside a packet. Such a scenario can therefore happen also with
only a single VLAN + 7 non-purgable addresses - requiring at least 120
bytes.

While this should be handled proactively when:

* interface with too low MTU is added
* VLAN is added
* non-purgeable local mac is added
* MTU of an attached interface is reduced
* fragmentation setting gets disabled (which most likely requires dropping
  attached interfaces)

not all of these scenarios can be prevented because batman-adv is only
consuming events without the the possibility to prevent these actions
(non-purgable MAC address added, MTU of an attached interface is reduced).
It is therefore necessary to also make sure that the code is able to handle
also the situations when there were already incompatible system
configuration are present.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/04720ea2e6c64459a90ca28570ea78335eccd924
- https://git.kernel.org/stable/c/3fe79b2c83461edbbf86ed8a6f3924820ff89259
- https://git.kernel.org/stable/c/4ca2a5fb54ea2cc43edea614207fcede562d91c2
- https://git.kernel.org/stable/c/70a8be9dc2fb65d67f8c1e0c88c587e08e2e575d
- https://git.kernel.org/stable/c/87b6af1a7683e021710c08fc0551fc078346032f
- https://git.kernel.org/stable/c/b1f532a3b1e6d2e5559c7ace49322922637a28aa
- https://git.kernel.org/stable/c/b3ddf6904073990492454b1dd1c10a24be8c74c6
- https://git.kernel.org/stable/c/ca54e2671548616ad34885f90d4f26f7adb088f0
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35982.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35982
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
