# [H] ksmbd: require minimum ACE size in smb_check_perm_dacl()

## Summary
Severity: High
Advisory: CVE-2026-31712
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31712
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: require minimum ACE size in smb_check_perm_dacl()

Both ACE-walk loops in smb_check_perm_dacl() only guard against an
under-sized remaining buffer, not against an ACE whose declared
`ace->size` is smaller than the struct it claims to describe:

  if (offsetof(struct smb_ace, access_req) > aces_size)
      break;
  ace_size = le16_to_cpu(ace->size);
  if (ace_size > aces_size)
      break;

The first check only requires the 4-byte ACE header to be in bounds;
it does not require access_req (4 bytes at offset 4) to be readable.
An attacker who has set a crafted DACL on a file they own can declare
ace->size == 4 with aces_size == 4, pass both checks, and then

  granted |= le32_to_cpu(ace->access_req);               /* upper loop */
  compare_sids(&sid, &ace->sid);                         /* lower loop */

reads access_req at offset 4 (OOB by up to 4 bytes) and ace->sid at
offset 8 (OOB by up to CIFS_SID_BASE_SIZE + SID_MAX_SUB_AUTHORITIES
* 4 bytes).

Tighten both loops to require

  ace_size >= offsetof(struct smb_ace, sid) + CIFS_SID_BASE_SIZE

which is the smallest valid on-wire ACE layout (4-byte header +
4-byte access_req + 8-byte sid base with zero sub-auths).  Also
reject ACEs whose sid.num_subauth exceeds SID_MAX_SUB_AUTHORITIES
before letting compare_sids() dereference sub_auth[] entries.

parse_sec_desc() already enforces an equivalent check (lines 441-448);
smb_check_perm_dacl() simply grew weaker validation over time.

Reachability: authenticated SMB client with permission to set an ACL
on a file.  On a subsequent CREATE against that file, the kernel
walks the stored DACL via smb_check_perm_dacl() and triggers the
OOB read.  Not pre-auth, and the OOB read is not reflected to the
attacker, but KASAN reports and kernel state corruption are
possible.

## References
- https://git.kernel.org/stable/c/151b1799861fde38087c08f613abc2843ef597b0
- https://git.kernel.org/stable/c/282cbbb476b9f35793452bc461934af4c7eca169
- https://git.kernel.org/stable/c/325d4ac11f526cb8964cff14548ccf02d8c756d8
- https://git.kernel.org/stable/c/90089584b2e25c4510b7b987387b4405f0673ece
- https://git.kernel.org/stable/c/95e5aa3c3261da8c95b27d7aecf8ee39b9f86a4c
- https://git.kernel.org/stable/c/d07b26f39246a82399661936dd0c853983cfade7
- https://git.kernel.org/stable/c/f20adc4ef7428bc485ee83fd1a592252fb87718b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31712.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
