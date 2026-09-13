# [H] powerpc/lib: Validate size for vector operations

## Summary
Severity: High
Advisory: CVE-2023-52606
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52606
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/lib: Validate size for vector operations

Some of the fp/vmx code in sstep.c assume a certain maximum size for the
instructions being emulated. The size of those operations however is
determined separately in analyse_instr().

Add a check to validate the assumption on the maximum size of the
operations, so as to prevent any unintended kernel stack corruption.

## References
- https://git.kernel.org/stable/c/0580f4403ad33f379eef865c2a6fe94de37febdf
- https://git.kernel.org/stable/c/28b8ba8eebf26f66d9f2df4ba550b6b3b136082c
- https://git.kernel.org/stable/c/42084a428a139f1a429f597d44621e3a18f3e414
- https://git.kernel.org/stable/c/848e1d7fd710900397e1d0e7584680c1c04e3afd
- https://git.kernel.org/stable/c/8f9abaa6d7de0a70fc68acaedce290c1f96e2e59
- https://git.kernel.org/stable/c/abd26515d4b767ba48241eea77b28ce0872aef3e
- https://git.kernel.org/stable/c/beee482cc4c9a6b1dcffb2e190b4fd8782258678
- https://git.kernel.org/stable/c/de4f5ed63b8a199704d8cdcbf810309d7eb4b36b
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52606.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
