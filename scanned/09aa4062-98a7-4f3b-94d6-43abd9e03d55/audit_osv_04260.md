# [H] BIT-ceph-2020-12059

## Summary
Severity: High
Advisory: BIT-ceph-2020-12059
Aliases: CVE-2020-12059
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2020-12059
Type: osv

## Affected
- Bitnami: `ceph` — affected unspecified

## Details
An issue was discovered in Ceph through 13.2.9. A POST request with an invalid tagging XML can crash the RGW process by triggering a NULL pointer exception.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1170170
- https://docs.ceph.com/docs/master/releases/mimic/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-12059
- https://tracker.ceph.com/issues/44967
- https://usn.ubuntu.com/4528-1/
