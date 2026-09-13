# [H] apparmor: validate DFA start states are in bounds in unpack_pdb

## Summary
Severity: High
Advisory: CVE-2026-23269
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23269
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: validate DFA start states are in bounds in unpack_pdb

Start states are read from untrusted data and used as indexes into the
DFA state tables. The aa_dfa_next() function call in unpack_pdb() will
access dfa->tables[YYTD_ID_BASE][start], and if the start state exceeds
the number of states in the DFA, this results in an out-of-bound read.

==================================================================
 BUG: KASAN: slab-out-of-bounds in aa_dfa_next+0x2a1/0x360
 Read of size 4 at addr ffff88811956fb90 by task su/1097
 ...

Reject policies with out-of-bounds start states during unpacking
to prevent the issue.

## References
- https://git.kernel.org/stable/c/07cf6320f40ea2ccfad63728cff34ecb309d03da
- https://git.kernel.org/stable/c/0baadb0eece2c4d939db10d3c323b4652ac79a58
- https://git.kernel.org/stable/c/15c3eb8916e7db01cb246d04a1fe6f0fdc065b0c
- https://git.kernel.org/stable/c/3bb7db43e32190c973d4019037cedb7895920184
- https://git.kernel.org/stable/c/5443c027ec16afa55b1b8a3e7a1ab2ea3c77767a
- https://git.kernel.org/stable/c/5487871b2b56c19d26936ed6fdc62652b30941df
- https://git.kernel.org/stable/c/9063d7e2615f4a7ab321de6b520e23d370e58816
- https://git.kernel.org/stable/c/f43eea8ae0102ea198da211ef7f5ce83725ecf19
- https://www.qualys.com/2026/03/10/crack-armor.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23269.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
