# [H] BIT-haproxy-2020-11100

## Summary
Severity: High
Advisory: BIT-haproxy-2020-11100
Aliases: CVE-2020-11100
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-haproxy-2020-11100
Type: osv

## Affected
- Bitnami: `haproxy` — affected >=1.8.0 <2.1.4

## Details
In hpack_dht_insert in hpack-tbl.c in the HPACK decoder in HAProxy 1.8 through 2.x before 2.1.4, a remote attacker can write arbitrary bytes around a certain location on the heap via a crafted HTTP/2 request, possibly causing remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00002.html
- http://packetstormsecurity.com/files/157323/haproxy-hpack-tbl.c-Out-Of-Bounds-Write.html
- http://www.haproxy.org
- https://bugzilla.redhat.com/show_bug.cgi?id=1819111
- https://bugzilla.suse.com/show_bug.cgi?id=1168023
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=5dfc5d5cd0d2128d77253ead3acf03a421ab5b88
- https://lists.debian.org/debian-security-announce/2020/msg00052.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/264C7UL3X7L7QE74ZJ557IOUFS3J4QQC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MNW5RZLIX7LOXRLV7WMHX22CI43XSXKW/
- https://security.gentoo.org/glsa/202012-22
- https://usn.ubuntu.com/4321-1/
- https://www.debian.org/security/2020/dsa-4649
- https://www.haproxy.org/download/2.1/src/CHANGELOG
- https://www.mail-archive.com/haproxy%40formilux.org/msg36876.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-11100
