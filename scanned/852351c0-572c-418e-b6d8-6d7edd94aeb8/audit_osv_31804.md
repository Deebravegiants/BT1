# [H] PCI: rcar-ep: Fix incorrect variable used when calling devm_request_mem_region()

## Summary
Severity: High
Advisory: CVE-2025-21804
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21804
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: rcar-ep: Fix incorrect variable used when calling devm_request_mem_region()

The rcar_pcie_parse_outbound_ranges() uses the devm_request_mem_region()
macro to request a needed resource. A string variable that lives on the
stack is then used to store a dynamically computed resource name, which
is then passed on as one of the macro arguments. This can lead to
undefined behavior.

Depending on the current contents of the memory, the manifestations of
errors may vary. One possible output may be as follows:

  $ cat /proc/iomem
  30000000-37ffffff :
  38000000-3fffffff :

Sometimes, garbage may appear after the colon.

In very rare cases, if no NULL-terminator is found in memory, the system
might crash because the string iterator will overrun which can lead to
access of unmapped memory above the stack.

Thus, fix this by replacing outbound_name with the name of the previously
requested resource. With the changes applied, the output will be as
follows:

  $ cat /proc/iomem
  30000000-37ffffff : memory2
  38000000-3fffffff : memory3

[kwilczynski: commit log]

## References
- https://git.kernel.org/stable/c/24576899c49509c0d533bcf569139f691d8f7af7
- https://git.kernel.org/stable/c/2c54b9fca1755e80a343ccfde0652dc5ea4744b2
- https://git.kernel.org/stable/c/2d2da5a4c1b4509f6f7e5a8db015cd420144beb4
- https://git.kernel.org/stable/c/44708208c2a4b828a57a2abe7799c9d3962e7eaa
- https://git.kernel.org/stable/c/6987e021b64cbb49981d140bb72d9d1466f191c4
- https://git.kernel.org/stable/c/7a47e14c5fb0b6dba7073be7b0119fb8fe864e01
- https://git.kernel.org/stable/c/9ff46b0bfeb6e0724a4ace015aa7a0b887cdb7c1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21804.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
