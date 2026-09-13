# [H] CVE-2019-9515

## Summary
Severity: High
Advisory: CVE-2019-9515
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/CVE-2019-9515
Type: osv

## Details
Some HTTP/2 implementations are vulnerable to a settings flood, potentially leading to a denial of service. The attacker sends a stream of SETTINGS frames to the peer. Since the RFC requires that the peer reply with one acknowledgement per SETTINGS frame, an empty SETTINGS frame is almost equivalent in behavior to a ping. Depending on how efficiently this data is queued, this can consume excess CPU, memory, or both.

## References
- https://lists.apache.org/thread.html/392108390cef48af647a2e47b7fd5380e050e35ae8d1aa2030254c04%40%3Cusers.trafficserver.apache.org%3E
- https://lists.apache.org/thread.html/ad3d01e767199c1aed8033bb6b3f5bf98c011c7c536f07a5d34b3c19%40%3Cannounce.trafficserver.apache.org%3E
- https://lists.apache.org/thread.html/bde52309316ae798186d783a5e29f4ad1527f61c9219a289d0eee0a7%40%3Cdev.trafficserver.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ZQGHE3WTYLYAYJEIDJVF2FIGQTAYPMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMNFX5MNYRWWIMO4BTKYQCGUDMHO3AXP/
- https://support.f5.com/csp/article/K50233772?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00032.html
- http://seclists.org/fulldisclosure/2019/Aug/16
- https://access.redhat.com/errata/RHSA-2019:2766
- https://access.redhat.com/errata/RHSA-2019:2796
- https://access.redhat.com/errata/RHSA-2019:2861
- https://access.redhat.com/errata/RHSA-2019:2925
- https://access.redhat.com/errata/RHSA-2019:2939
- https://access.redhat.com/errata/RHSA-2019:2955
- https://access.redhat.com/errata/RHSA-2019:3892
- https://access.redhat.com/errata/RHSA-2019:4018
- https://access.redhat.com/errata/RHSA-2019:4019
- https://access.redhat.com/errata/RHSA-2019:4020
- https://access.redhat.com/errata/RHSA-2019:4021
