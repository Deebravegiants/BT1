# [H] smb: client: require a full NFS mode SID before reading mode bits

## Summary
Severity: High
Advisory: CVE-2026-43350
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43350
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: require a full NFS mode SID before reading mode bits

parse_dacl() treats an ACE SID matching sid_unix_NFS_mode as an NFS
mode SID and reads sid.sub_auth[2] to recover the mode bits.

That assumes the ACE carries three subauthorities, but compare_sids()
only compares min(a, b) subauthorities.  A malicious server can return
an ACE with num_subauth = 2 and sub_auth[] = {88, 3}, which still
matches sid_unix_NFS_mode and then drives the sub_auth[2] read four
bytes past the end of the ACE.

Require num_subauth >= 3 before treating the ACE as an NFS mode SID.
This keeps the fix local to the special-SID mode path without changing
compare_sids() semantics for the rest of cifsacl.

## References
- https://git.kernel.org/stable/c/1592a6cd6f653f2d24572a6976c7a775b19f4940
- https://git.kernel.org/stable/c/23b54d6cc3ef30a51d984dc74364f24039ae2ecb
- https://git.kernel.org/stable/c/2757ad3e4b6f9e0fed4c7739594e702abc5cab21
- https://git.kernel.org/stable/c/38a69f08ee82c450d3e4168707fff2e317dc3ff7
- https://git.kernel.org/stable/c/8bd4cad3f458d11650d51c2d24b03fb1770ae6cc
- https://git.kernel.org/stable/c/b53b8e98c23310294fc45fc686db5ee860311896
- https://git.kernel.org/stable/c/c8eef12af1cc73031639ea7cf16e0b10e2536b0b
- https://git.kernel.org/stable/c/f8488c07bea2431ee12a6067d736578064fa46b4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43350.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
