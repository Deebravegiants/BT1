# [H] smb: client: validate the whole DACL before rewriting it in cifsacl

## Summary
Severity: High
Advisory: CVE-2026-31709
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31709
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.35, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: validate the whole DACL before rewriting it in cifsacl

build_sec_desc() and id_mode_to_cifs_acl() derive a DACL pointer from a
server-supplied dacloffset and then use the incoming ACL to rebuild the
chmod/chown security descriptor.

The original fix only checked that the struct smb_acl header fits before
reading dacl_ptr->size or dacl_ptr->num_aces.  That avoids the immediate
header-field OOB read, but the rewrite helpers still walk ACEs based on
pdacl->num_aces with no structural validation of the incoming DACL body.

A malicious server can return a truncated DACL that still contains a
header, claims one or more ACEs, and then drive
replace_sids_and_copy_aces() or set_chmod_dacl() past the validated
extent while they compare or copy attacker-controlled ACEs.

Factor the DACL structural checks into validate_dacl(), extend them to
validate each ACE against the DACL bounds, and use the shared validator
before the chmod/chown rebuild paths.  parse_dacl() reuses the same
validator so the read-side parser and write-side rewrite paths agree on
what constitutes a well-formed incoming DACL.

## References
- https://git.kernel.org/stable/c/0a8cf165566ba55a39fd0f4de172119dd646d39a
- https://git.kernel.org/stable/c/8e47d297e7cf9a6029a0d38e7b22faba7d7aaf12
- https://git.kernel.org/stable/c/b78db9bddc84136f6a0bb49e8883cf200dfb87a8
- https://git.kernel.org/stable/c/b8603d9ae6c9087662b098619996bc4a8064319d
- https://git.kernel.org/stable/c/c2abdebf72000a64603ced84d36ccbd164f11391
- https://git.kernel.org/stable/c/d92f3f0b22414e7515696a02224d0af55e3004a3
- https://git.kernel.org/stable/c/ff0ca46b13b9ef6edbcd238a3b6caacfef8ba0e5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31709.json
- https://access.redhat.com/errata/RHSA-2026:21556
- https://access.redhat.com/errata/RHSA-2026:21706
- https://access.redhat.com/errata/RHSA-2026:21745
- https://access.redhat.com/errata/RHSA-2026:22900
- https://access.redhat.com/errata/RHSA-2026:22940
- https://access.redhat.com/errata/RHSA-2026:23224
- https://access.redhat.com/errata/RHSA-2026:23237
- https://access.redhat.com/errata/RHSA-2026:23329
- https://access.redhat.com/errata/RHSA-2026:24343
- https://access.redhat.com/security/cve/CVE-2026-31709
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31709.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31709
