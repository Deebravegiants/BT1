# [C] x86/sev: Evict cache lines during SNP memory validation

## Summary
Severity: Critical
Advisory: CVE-2025-38560
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38560
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/sev: Evict cache lines during SNP memory validation

An SNP cache coherency vulnerability requires a cache line eviction
mitigation when validating memory after a page state change to private.
The specific mitigation is to touch the first and last byte of each 4K
page that is being validated. There is no need to perform the mitigation
when performing a page state change to shared and rescinding validation.

CPUID bit Fn8000001F_EBX[31] defines the COHERENCY_SFW_NO CPUID bit
that, when set, indicates that the software mitigation for this
vulnerability is not needed.

Implement the mitigation and invoke it when validating memory (making it
private) and the COHERENCY_SFW_NO bit is not set, indicating the SNP
guest is vulnerable.

## References
- https://git.kernel.org/stable/c/1fb873971e23c35c53823c62809a474a92bc3022
- https://git.kernel.org/stable/c/1fec416c03d0a64cc21aa04ce4aa14254b017e6a
- https://git.kernel.org/stable/c/7b306dfa326f70114312b320d083b21fa9481e1e
- https://git.kernel.org/stable/c/a762a4c8d9e768b538b3cc60615361a8cf377de8
- https://git.kernel.org/stable/c/aed15fc08f15dbb15822b2a0b653f67e76aa0fdf
- https://git.kernel.org/stable/c/f92af52e6dbd8d066d77beba451e0230482dc45b
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38560.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38560
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
