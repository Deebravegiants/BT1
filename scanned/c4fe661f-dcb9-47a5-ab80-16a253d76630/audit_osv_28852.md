# [H] remoteproc: mediatek: Make sure IPI buffer fits in L2TCM

## Summary
Severity: High
Advisory: CVE-2024-36965
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-08
Source: https://osv.dev/vulnerability/CVE-2024-36965
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.160, >=5.16.0 <6.1.92, >=6.2.0 <6.6.32, >=6.7.0 <6.8.11, >=6.9.0 <6.9.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

remoteproc: mediatek: Make sure IPI buffer fits in L2TCM

The IPI buffer location is read from the firmware that we load to the
System Companion Processor, and it's not granted that both the SRAM
(L2TCM) size that is defined in the devicetree node is large enough
for that, and while this is especially true for multi-core SCP, it's
still useful to check on single-core variants as well.

Failing to perform this check may make this driver perform R/W
operations out of the L2TCM boundary, resulting (at best) in a
kernel panic.

To fix that, check that the IPI buffer fits, otherwise return a
failure and refuse to boot the relevant SCP core (or the SCP at
all, if this is single core).

## References
- https://git.kernel.org/stable/c/00548ac6b14428719c970ef90adae2b3b48c0cdf
- https://git.kernel.org/stable/c/1d9e2de24533daca36cbf09e8d8596bf72b526b2
- https://git.kernel.org/stable/c/26c6d7dc8c6a9fde9d362ab2eef6390efeff145e
- https://git.kernel.org/stable/c/331f91d86f71d0bb89a44217cc0b2a22810bbd42
- https://git.kernel.org/stable/c/36c79eb4845551e9f6d28c663b38ce0ab03b84a9
- https://git.kernel.org/stable/c/838b49e211d59fa827ff9df062d4020917cffbdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36965.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36965
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
