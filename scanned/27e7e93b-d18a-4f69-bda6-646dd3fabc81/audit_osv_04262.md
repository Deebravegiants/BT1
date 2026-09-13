# [M] BIT-ceph-2020-1759

## Summary
Severity: Medium
Advisory: BIT-ceph-2020-1759
Aliases: CVE-2020-1759
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2020-1759
Type: osv

## Affected
- Bitnami: `ceph` — affected >=0 <14.2.21

## Details
A vulnerability was found in Red Hat Ceph Storage 4 and Red Hat Openshift Container Storage 4.2 where, A nonce reuse vulnerability was discovered in the secure mode of the messenger v2 protocol, which can allow an attacker to forge auth tags and potentially manipulate the data by leveraging the reuse of a nonce in a session. Messages encrypted using a reused nonce value are susceptible to serious confidentiality and integrity attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1759
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P3A2UFR5IUIEXJUCF64GQ5OVLCZGODXE/
- https://nvd.nist.gov/vuln/detail/CVE-2020-1759
- https://security.gentoo.org/glsa/202105-39
