# [H] padata: use integer wrap around to prevent deadlock on seq_nr overflow

## Summary
Severity: High
Advisory: CVE-2024-47739
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47739
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

padata: use integer wrap around to prevent deadlock on seq_nr overflow

When submitting more than 2^32 padata objects to padata_do_serial, the
current sorting implementation incorrectly sorts padata objects with
overflowed seq_nr, causing them to be placed before existing objects in
the reorder list. This leads to a deadlock in the serialization process
as padata_find_next cannot match padata->seq_nr and pd->processed
because the padata instance with overflowed seq_nr will be selected
next.

To fix this, we use an unsigned integer wrap around to correctly sort
padata objects in scenarios with integer overflow.

## References
- https://git.kernel.org/stable/c/1b8cf11b3ca593a8802a51802cd0c28c38501428
- https://git.kernel.org/stable/c/1bd712de96ad7167fe0d608e706cd60587579f16
- https://git.kernel.org/stable/c/46c4079460f4dcaf445860679558eedef4e1bc91
- https://git.kernel.org/stable/c/72164d5b648951684b1a593996b37a6083c61d7d
- https://git.kernel.org/stable/c/9a22b2812393d93d84358a760c347c21939029a6
- https://git.kernel.org/stable/c/9e279e6c1f012b82628b89e1b9c65dbefa8ca25a
- https://git.kernel.org/stable/c/ab205e1c3846326f162180e56825b4ba38ce9c30
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47739.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
