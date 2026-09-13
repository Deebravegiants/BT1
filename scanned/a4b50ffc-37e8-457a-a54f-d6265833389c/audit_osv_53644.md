# [M] CVE-2023-1193

## Summary
Severity: Medium
Advisory: CVE-2023-1193
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-1193
Type: osv

## Details
A use-after-free flaw was found in setup_async_work in the KSMBD implementation of the in-kernel samba server and CIFS in the Linux kernel. This issue could allow an attacker to crash the system by accessing freed work.

## References
- https://access.redhat.com/security/cve/CVE-2023-1193
- https://bugzilla.redhat.com/show_bug.cgi?id=2154177
- https://lkml.kernel.org/linux-cifs/20230401084951.6085-2-linkinjeon@kernel.org/T/
