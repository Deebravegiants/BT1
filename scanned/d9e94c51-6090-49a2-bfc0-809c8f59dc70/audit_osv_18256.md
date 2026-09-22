# [H] CVE-2020-25660

## Summary
Severity: High
Advisory: CVE-2020-25660
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-25660
Type: osv

## Details
A flaw was found in the Cephx authentication protocol in versions before 15.2.6 and before 14.2.14, where it does not verify Ceph clients correctly and is then vulnerable to replay attacks in Nautilus. This flaw allows an attacker with access to the Ceph cluster network to authenticate with the Ceph service via a packet sniffer and perform actions allowed by the Ceph service. This issue is a reintroduction of CVE-2018-1128, affecting the msgr2 protocol. The msgr 2 protocol is used for all communication except older clients that do not support the msgr2 protocol. The msgr1 protocol is not affected. The highest threat from this vulnerability is to confidentiality, integrity, and system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UBC4KZ44QUQENTYZPVHORGL4K2KV5V4F/
- https://ceph.io/community/v15-2-6-octopus-released/
- https://ceph.io/releases/v14-2-14-nautilus-released/
- https://security.gentoo.org/glsa/202105-39
- https://bugzilla.redhat.com/show_bug.cgi?id=1890354
