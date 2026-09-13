# [H] powerpc/powernv: Add a null pointer check in opal_powercap_init()

## Summary
Severity: High
Advisory: CVE-2023-52696
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52696
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/powernv: Add a null pointer check in opal_powercap_init()

kasprintf() returns a pointer to dynamically allocated memory
which can be NULL upon failure.

## References
- https://git.kernel.org/stable/c/69f95c5e9220f77ce7c540686b056c2b49e9a664
- https://git.kernel.org/stable/c/6b58d16037217d0c64a2a09b655f370403ec7219
- https://git.kernel.org/stable/c/9da4a56dd3772570512ca58aa8832b052ae910dc
- https://git.kernel.org/stable/c/a67a04ad05acb56640798625e73fa54d6d41cce1
- https://git.kernel.org/stable/c/b02ecc35d01a76b4235e008d2dd292895b28ecab
- https://git.kernel.org/stable/c/e123015c0ba859cf48aa7f89c5016cc6e98e018d
- https://git.kernel.org/stable/c/f152a6bfd187f67afeffc9fd68cbe46f51439be0
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52696.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
