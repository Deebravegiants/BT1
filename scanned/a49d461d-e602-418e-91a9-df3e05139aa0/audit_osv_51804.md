# [H] CVE-2021-4090

## Summary
Severity: High
Advisory: CVE-2021-4090
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-4090
Type: osv

## Details
An out-of-bounds (OOB) memory write flaw was found in the NFSD in the Linux kernel. Missing sanity may lead to a write beyond bmval[bmlen-1] in nfsd4_decode_bitmap4 in fs/nfsd/nfs4xdr.c. In this flaw, a local attacker with user privilege may gain access to out-of-bounds memory, leading to a system integrity and confidentiality threat.

## References
- https://lore.kernel.org/linux-nfs/163692036074.16710.5678362976688977923.stgit%40klimt.1015granger.net/
- https://security.netapp.com/advisory/ntap-20220318-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=2025101
