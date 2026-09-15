# [H] CVE-2018-20406

## Summary
Severity: High
Advisory: CVE-2018-20406
Aliases: PSF-2018-6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/CVE-2018-20406
Type: osv

## Details
Modules/_pickle.c in Python before 3.7.1 has an integer overflow via a large LONG_BINPUT value that is mishandled during a "resize to twice the size" attempt. This issue might cause memory exhaustion, but is only relevant if the pickle format is used for serializing tens or hundreds of gigabytes of data. This issue is fixed in: v3.4.10, v3.4.10rc1; v3.5.10, v3.5.10rc1, v3.5.7, v3.5.7rc1, v3.5.8, v3.5.8rc1, v3.5.8rc2, v3.5.9; v3.6.10, v3.6.10rc1, v3.6.11, v3.6.11rc1, v3.6.12, v3.6.7, v3.6.7rc1, v3.6.7rc2, v3.6.8, v3.6.8rc1, v3.6.9, v3.6.9rc1; v3.7.1, v3.7.1rc1, v3.7.1rc2, v3.7.2, v3.7.2rc1, v3.7.3, v3.7.3rc1, v3.7.4, v3.7.4rc1, v3.7.4rc2, v3.7.5, v3.7.5rc1, v3.7.6, v3.7.6rc1, v3.7.7, v3.7.7rc1, v3.7.8, v3.7.8rc1, v3.7.9.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/46PVWY5LFP4BRPG3BVQ5QEEFYBVEXHCK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AEZ5IQT7OF7Q2NCGIVABOWYGKO7YU3NJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D3LXPABKVLFYUHRYJPM3CSS5MS6FXKS7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ICBEGRHIPHWPG2VGYS6R4EVKVUUF4AQW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JSKPGPZQNTAULHW4UH63KGOOUIDE4RRB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TR6GCO3WTV4D5L23WTCBF275VE6BVNI3/
- https://usn.ubuntu.com/4127-1/
- https://usn.ubuntu.com/4127-2/
- https://access.redhat.com/errata/RHSA-2019:3725
- https://lists.debian.org/debian-lts-announce/2019/02/msg00011.html
- https://security.netapp.com/advisory/ntap-20190416-0010/
- https://bugs.python.org/issue34656
- https://github.com/python/cpython/commit/a4ae828ee416a66d8c7bf5ee71d653c2cc6a26dd
