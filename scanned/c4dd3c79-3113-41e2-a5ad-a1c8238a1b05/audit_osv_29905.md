# [H] PCI: keystone: Add workaround for Errata #i2037 (AM65x SR 1.0)

## Summary
Severity: High
Advisory: CVE-2024-47667
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47667
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: keystone: Add workaround for Errata #i2037 (AM65x SR 1.0)

Errata #i2037 in AM65x/DRA80xM Processors Silicon Revision 1.0
(SPRZ452D_July 2018_Revised December 2019 [1]) mentions when an
inbound PCIe TLP spans more than two internal AXI 128-byte bursts,
the bus may corrupt the packet payload and the corrupt data may
cause associated applications or the processor to hang.

The workaround for Errata #i2037 is to limit the maximum read
request size and maximum payload size to 128 bytes. Add workaround
for Errata #i2037 here.

The errata and workaround is applicable only to AM65x SR 1.0 and
later versions of the silicon will have this fixed.

[1] -> https://www.ti.com/lit/er/sprz452i/sprz452i.pdf

## References
- https://git.kernel.org/stable/c/135843c351c08df72bdd4b4ebea53c8052a76881
- https://git.kernel.org/stable/c/576d0fb6f8d4bd4695e70eee173a1b9c7bae9572
- https://git.kernel.org/stable/c/86f271f22bbb6391410a07e08d6ca3757fda01fa
- https://git.kernel.org/stable/c/af218c803fe298ddf00abef331aa526b20d7ea61
- https://git.kernel.org/stable/c/cfb006e185f64edbbdf7869eac352442bc76b8f6
- https://git.kernel.org/stable/c/dd47051c76c8acd8cb983f01b4d1265da29cb66a
- https://git.kernel.org/stable/c/ebbdbbc580c1695dec283d0ba6448729dc993246
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47667.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
