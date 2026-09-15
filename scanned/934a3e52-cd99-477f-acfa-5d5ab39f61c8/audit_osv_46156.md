# [H] In OpenSSH before 10.3, a file downloaded by scp may be installed setuid or setgid, an outcome...

## Summary
Severity: High
Advisory: JLSEC-2026-74
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-74
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.3.1+0

## Details
In OpenSSH before 10.3, a file downloaded by scp may be installed setuid or setgid, an outcome contrary to some users' expectations, if the download is performed as root with -O (legacy scp protocol) and without -p (preserve mode).

## References
- https://access.redhat.com/errata/RHSA-2026:12389
- https://access.redhat.com/errata/RHSA-2026:13380
- https://access.redhat.com/errata/RHSA-2026:13381
- https://access.redhat.com/errata/RHSA-2026:13383
- https://access.redhat.com/errata/RHSA-2026:14937
- https://access.redhat.com/errata/RHSA-2026:16059
- https://access.redhat.com/errata/RHSA-2026:19069
- https://access.redhat.com/errata/RHSA-2026:19219
- https://access.redhat.com/errata/RHSA-2026:20040
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:21298
- https://access.redhat.com/errata/RHSA-2026:21398
- https://access.redhat.com/errata/RHSA-2026:22329
- https://access.redhat.com/errata/RHSA-2026:22468
- https://access.redhat.com/errata/RHSA-2026:22564
- https://access.redhat.com/errata/RHSA-2026:22648
- https://access.redhat.com/errata/RHSA-2026:25044
- https://access.redhat.com/errata/RHSA-2026:25063
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:25181
