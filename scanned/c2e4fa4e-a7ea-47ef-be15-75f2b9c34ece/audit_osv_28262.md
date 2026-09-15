# [M] Booth: specially crafted hash can lead to invalid hmac being accepted by booth server

## Summary
Severity: Medium
Advisory: CVE-2024-3049
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3049
Type: osv

## Details
A flaw was found in Booth, a cluster ticket manager. If a specially-crafted hash is passed to gcry_md_get_algo_dlen(), it may allow an invalid HMAC to be accepted by the Booth server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/09/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ERCFM3HXFJKLEMMWU3CZLPKH5LZAEDAN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KPK5BHYOB7CFFRQAN55YV5LH44PWHMQD/
- https://access.redhat.com/errata/RHSA-2024:3657
- https://access.redhat.com/errata/RHSA-2024:3658
- https://access.redhat.com/errata/RHSA-2024:3659
- https://access.redhat.com/errata/RHSA-2024:3660
- https://access.redhat.com/errata/RHSA-2024:3661
- https://access.redhat.com/errata/RHSA-2024:4400
- https://access.redhat.com/errata/RHSA-2024:4411
- https://access.redhat.com/security/cve/CVE-2024-3049
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3049.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3049
- https://bugzilla.redhat.com/show_bug.cgi?id=2272082
- https://github.com/ClusterLabs/booth/pull/142
- https://github.com/ClusterLabs/booth
