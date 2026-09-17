# [H] xfrm: xfrm_alloc_spi shouldn't use 0 as SPI

## Summary
Severity: High
Advisory: CVE-2025-39965
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-39965
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.103 <6.6.109, >=6.12.43 <6.12.50, >=6.16.2 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: xfrm_alloc_spi shouldn't use 0 as SPI

x->id.spi == 0 means "no SPI assigned", but since commit
94f39804d891 ("xfrm: Duplicate SPI Handling"), we now create states
and add them to the byspi list with this value.

__xfrm_state_delete doesn't remove those states from the byspi list,
since they shouldn't be there, and this shows up as a UAF the next
time we go through the byspi list.

## References
- https://git.kernel.org/stable/c/0baf92d0b1590b903c1f4ead75e61715e50e8146
- https://git.kernel.org/stable/c/9fcedabaae0096f712bbb4ccca6a8538af1cd1c8
- https://git.kernel.org/stable/c/a78e55776522373c446f18d5002a8de4b09e6bf7
- https://git.kernel.org/stable/c/cd8ae32e4e4652db55bce6b9c79267d8946765a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39965.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39965
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
