# [M] ext4: Fix function prototype mismatch for ext4_feat_ktype

## Summary
Severity: Medium
Advisory: CVE-2023-53224
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53224
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.274, >=4.20.0 <5.4.233, >=5.5.0 <5.10.170, >=5.11.0 <5.15.96, >=5.16.0 <6.1.14, >=6.2.0 <6.2.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: Fix function prototype mismatch for ext4_feat_ktype

With clang's kernel control flow integrity (kCFI, CONFIG_CFI_CLANG),
indirect call targets are validated against the expected function
pointer prototype to make sure the call target is valid to help mitigate
ROP attacks. If they are not identical, there is a failure at run time,
which manifests as either a kernel panic or thread getting killed.

ext4_feat_ktype was setting the "release" handler to "kfree", which
doesn't have a matching function prototype. Add a simple wrapper
with the correct prototype.

This was found as a result of Clang's new -Wcast-function-type-strict
flag, which is more sensitive than the simpler -Wcast-function-type,
which only checks for type width mismatches.

Note that this code is only reached when ext4 is a loadable module and
it is being unloaded:

 CFI failure at kobject_put+0xbb/0x1b0 (target: kfree+0x0/0x180; expected type: 0x7c4aa698)
 ...
 RIP: 0010:kobject_put+0xbb/0x1b0
 ...
 Call Trace:
  <TASK>
  ext4_exit_sysfs+0x14/0x60 [ext4]
  cleanup_module+0x67/0xedb [ext4]

## References
- https://git.kernel.org/stable/c/0a1394e07c5d6bf1bfc25db8589ff1b1bfb6f46a
- https://git.kernel.org/stable/c/118901ad1f25d2334255b3d50512fa20591531cd
- https://git.kernel.org/stable/c/1ba10d3640e9783dad811fe4e24d55465c37c64d
- https://git.kernel.org/stable/c/2b69cdd9f9a7f596e3dd31f05f9852940d177924
- https://git.kernel.org/stable/c/94d8de83286fb1827340eba35b61c308f6b46ead
- https://git.kernel.org/stable/c/99e3fd21f8fc975c95e8cf76fbf6a3d2656f8f71
- https://git.kernel.org/stable/c/c98077f7598a562f51051eec043be0cb3e1b1b5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53224.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53224
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
