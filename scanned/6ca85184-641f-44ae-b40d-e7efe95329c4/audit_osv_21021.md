# [M] CVE-2021-3979

## Summary
Severity: Medium
Advisory: CVE-2021-3979
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-3979
Type: osv

## Details
A key length flaw was found in Red Hat Ceph Storage. An attacker can exploit the fact that the key length is incorrectly passed in an encryption algorithm to create a non random key, which is weaker and can be exploited for loss of confidentiality and integrity on encrypted disks.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.debian.org/debian-lts-announce/2025/09/msg00025.html
- https://access.redhat.com/security/cve/CVE-2021-3979
- https://bugzilla.redhat.com/show_bug.cgi?id=2024788
- https://tracker.ceph.com/issues/54006
- https://github.com/ceph/ceph/commit/47c33179f9a15ae95cc1579a421be89378602656
- https://github.com/ceph/ceph/pull/44765
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BPOK44BESMIFW6BIOGCN452AKKOIIT6Q/
