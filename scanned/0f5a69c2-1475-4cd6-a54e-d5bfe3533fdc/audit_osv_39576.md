# [C] smb: client: validate dacloffset before building DACL pointers

## Summary
Severity: Critical
Advisory: CVE-2026-46195
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46195
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: validate dacloffset before building DACL pointers

parse_sec_desc(), build_sec_desc(), and the chown path in
id_mode_to_cifs_acl() all add the server-supplied dacloffset to pntsd
before proving a DACL header fits inside the returned security
descriptor.

On 32-bit builds a malicious server can return dacloffset near
U32_MAX, wrap the derived DACL pointer below end_of_acl, and then slip
past the later pointer-based bounds checks. build_sec_desc() and
id_mode_to_cifs_acl() can then dereference DACL fields from the wrapped
pointer in the chmod/chown rewrite paths.

Validate dacloffset numerically before building any DACL pointer and
reuse the same helper at the three DACL entry points.

## References
- https://git.kernel.org/stable/c/3b1ddba19e77ee35241cd27f16dc3e8d14e08db7
- https://git.kernel.org/stable/c/5de2665e913a10ad70aaeecf736b97276e83d995
- https://git.kernel.org/stable/c/8bd07e417b6bda67e317920584e48cb6ee442a8a
- https://git.kernel.org/stable/c/ba7f71b6161c0943dafc367565e5843d16b7d505
- https://git.kernel.org/stable/c/c688f3ed73d31943334ad2139cb02ec49664322a
- https://git.kernel.org/stable/c/f98b48151cc502ada59d9778f0112d21f2586ca3
- https://git.kernel.org/stable/c/f9dc3be8f403c1216df73e57221f44b045e7ee0b
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46195.json
- https://access.redhat.com/errata/RHSA-2026:21556
- https://access.redhat.com/errata/RHSA-2026:21706
- https://access.redhat.com/errata/RHSA-2026:21745
- https://access.redhat.com/security/cve/CVE-2026-46195
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46195.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46195
- https://bugzilla.redhat.com/show_bug.cgi?id=2482606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
