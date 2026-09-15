# [H] mm: avoid leaving partial pfn mappings around in error case

## Summary
Severity: High
Advisory: CVE-2024-47674
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-47674
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.168, >=5.16.0 <6.1.111, >=6.2.0 <6.6.52, >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: avoid leaving partial pfn mappings around in error case

As Jann points out, PFN mappings are special, because unlike normal
memory mappings, there is no lifetime information associated with the
mapping - it is just a raw mapping of PFNs with no reference counting of
a 'struct page'.

That's all very much intentional, but it does mean that it's easy to
mess up the cleanup in case of errors.  Yes, a failed mmap() will always
eventually clean up any partial mappings, but without any explicit
lifetime in the page table mapping itself, it's very easy to do the
error handling in the wrong order.

In particular, it's easy to mistakenly free the physical backing store
before the page tables are actually cleaned up and (temporarily) have
stale dangling PTE entries.

To make this situation less error-prone, just make sure that any partial
pfn mapping is torn down early, before any other error handling.

## References
- https://git.kernel.org/stable/c/3213fdcab961026203dd587a4533600c70b3336b
- https://git.kernel.org/stable/c/35770ca6180caa24a2b258c99a87bd437a1ee10f
- https://git.kernel.org/stable/c/5b2c8b34f6d76bfbd1dd4936eb8a0fbfb9af3959
- https://git.kernel.org/stable/c/65d0db500d7c07f0f76fc24a4d837791c4862cd2
- https://git.kernel.org/stable/c/79a61cc3fc0466ad2b7b89618a6157785f0293b3
- https://git.kernel.org/stable/c/954fd4c81f22c4b6ba65379a81fd252971bf4ef3
- https://git.kernel.org/stable/c/a95a24fcaee1b892e47d5e6dcc403f713874ee80
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://project-zero.issues.chromium.org/issues/366053091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47674.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
