# [H] BIT-ceph-2021-20288

## Summary
Severity: High
Advisory: BIT-ceph-2021-20288
Aliases: CVE-2021-20288
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2021-20288
Type: osv

## Affected
- Bitnami: `ceph` — affected >=0 <14.2.21

## Details
An authentication flaw was found in ceph in versions before 14.2.20. When the monitor handles CEPHX_GET_AUTH_SESSION_KEY requests, it doesn't sanitize other_keys, allowing key reuse. An attacker who can request a global_id can exploit the ability of any user to request a global_id previously associated with another user, as ceph does not force the reuse of old keys to generate new ones. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1938031
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/362CEPPYF3YMJZBEJQUT3KDE2EHYYIYQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5BPIAYTRCWAU4XWCDBK2THEFVXSC4XGK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JVWUKUUS5BCIFWRV3JCUQMAPJ4HIWSED/
- https://nvd.nist.gov/vuln/detail/CVE-2021-20288
- https://security.gentoo.org/glsa/202105-39
