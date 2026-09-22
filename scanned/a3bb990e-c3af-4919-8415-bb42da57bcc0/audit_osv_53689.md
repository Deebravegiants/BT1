# [H] CVE-2023-1652

## Summary
Severity: High
Advisory: CVE-2023-1652
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2023-1652
Type: osv

## Details
A use-after-free flaw was found in nfsd4_ssc_setup_dul in fs/nfsd/nfs4proc.c in the NFS filesystem in the Linux Kernel. This issue could allow a local attacker to crash the system or it may lead to a kernel information leak problem.

## References
- https://security.netapp.com/advisory/ntap-20230511-0006/
- https://access.redhat.com/security/cve/cve-2023-1652
