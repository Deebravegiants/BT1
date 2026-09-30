# [H] libceph: handle rbtree insertion error in decode_choose_args()

## Summary
Severity: High
Advisory: CVE-2026-52954
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52954
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: handle rbtree insertion error in decode_choose_args()

A message of type CEPH_MSG_OSD_MAP contains an OSD map that itself
contains a CRUSH map. The received CRUSH map may optionally contain
choose_args that get decoded in decode_choose_args(). In this function,
num_choose_arg_maps is read from the message, and a corresponding number
of crush_choose_arg_maps gets decoded afterwards. Each
crush_choose_arg_map has a choose_args_index, which serves as the key
when inserting it into the choose_args rbtree of the decoded crush_map.
If a (potentially corrupted) message contains two crush_choose_arg_maps
with the same index, the assertion in insert_choose_arg_map() triggers a
kernel BUG when trying to insert the second crush_choose_arg_map.

This patch fixes the issue by switching to the non-asserting rbtree
insertion function and rejecting the message if the insertion fails.

[ idryomov: changelog ]

## References
- https://git.kernel.org/stable/c/0a1265a9ab875f92b6a3ffb497404f46cf9d76a3
- https://git.kernel.org/stable/c/0b6a3bcb91bc5bfeda39f0df3b71bab62c13e9da
- https://git.kernel.org/stable/c/4d2b37abda9536808655830d683dc491d31741a8
- https://git.kernel.org/stable/c/534ebc08df97c47d4c7596f336fa31ecbf91519c
- https://git.kernel.org/stable/c/80c73bd1b2b04355d1d0c29be8ccbd25a380905d
- https://git.kernel.org/stable/c/c7bf7864e2924fa5508ac270b0e9364bc13d5a6c
- https://git.kernel.org/stable/c/d289478cfc0bcf81c7914200d6abdcb78bd04ded
- https://git.kernel.org/stable/c/f47430fc1f815e87406e2d3b4e476eff1bc7fd9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52954.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
