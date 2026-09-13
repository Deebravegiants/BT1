# [H] ftrace: Also allocate and copy hash for reading of filter files

## Summary
Severity: High
Advisory: CVE-2025-39689
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39689
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Also allocate and copy hash for reading of filter files

Currently the reader of set_ftrace_filter and set_ftrace_notrace just adds
the pointer to the global tracer hash to its iterator. Unlike the writer
that allocates a copy of the hash, the reader keeps the pointer to the
filter hashes. This is problematic because this pointer is static across
function calls that release the locks that can update the global tracer
hashes. This can cause UAF and similar bugs.

Allocate and copy the hash for reading the filter files like it is done
for the writers. This not only fixes UAF bugs, but also makes the code a
bit simpler as it doesn't have to differentiate when to free the
iterator's hash between writers and readers.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/12064e1880fc9202be75ff668205b1703d92f74f
- https://git.kernel.org/stable/c/3b114a3282ab1a12cb4618a8f45db5d7185e784a
- https://git.kernel.org/stable/c/64db338140d2bad99a0a8c6a118dd60b3e1fb8cb
- https://git.kernel.org/stable/c/a40c69f4f1ed96acbcd62e9b5ff3a596f0a91309
- https://git.kernel.org/stable/c/bfb336cf97df7b37b2b2edec0f69773e06d11955
- https://git.kernel.org/stable/c/c4cd93811e038d19f961985735ef7bb128078dfb
- https://git.kernel.org/stable/c/c591ba1acd081d4980713e47869dd1cc3d963d19
- https://git.kernel.org/stable/c/e0b6b223167e1edde5c82edf38e393c06eda1f13
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39689.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39689
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
