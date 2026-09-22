# [C] BIT-ceph-2022-0670

## Summary
Severity: Critical
Advisory: BIT-ceph-2022-0670
Aliases: CVE-2022-0670
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2022-0670
Type: osv

## Affected
- Bitnami: `ceph` — affected >=17.0.0 <17.2.2

## Details
A flaw was found in Openstack manilla owning a Ceph File system "share", which enables the owner to read/write any manilla share or entire file system. The vulnerability is due to a bug in the "volumes" plugin in Ceph Manager. This allows an attacker to compromise Confidentiality and Integrity of a file system. Fixed in RHCS 5.2 and Ceph 17.2.2.

## References
- https://ceph.io/en/news/blog/2022/v17-2-2-quincy-released/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5O3XMDFZWA2FWU6GAYOVSFJPOUTXN42N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TIRTTRG5O4YP2TNGDCDOHIHP2DM3DFBT/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0670
