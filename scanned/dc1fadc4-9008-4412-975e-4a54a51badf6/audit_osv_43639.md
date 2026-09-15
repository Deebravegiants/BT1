# [H] KVM: s390: pci: Reject adapter interrupt forwarding if already enabled

## Summary
Severity: High
Advisory: CVE-2026-74515
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74515
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: pci: Reject adapter interrupt forwarding if already enabled

The MPCIFC instruction doesn't allow registering adapter interrupts without
first unregistering. So reject any request to enable interrupt forwarding
if its already enabled for the zPCI device. This also fixes overwriting and
thus leaking resources when the ioctl is called multiple times for the same
device.

## References
- https://git.kernel.org/stable/c/591952b63a9f976da7d49f719f36ec826ee2a575
- https://git.kernel.org/stable/c/642d2d1067f7c4d753ae0e3ba5bc98b43cfe3c70
- https://git.kernel.org/stable/c/6837f0ae85fd54cf64c8a0c7c530bba2fae0a207
- https://git.kernel.org/stable/c/6be1ff49ba81f96a6fa55915e6d920be43ac57cc
- https://git.kernel.org/stable/c/78d9648e7e960546d5b72504a0b0358cd8bb1e9d
- https://git.kernel.org/stable/c/8fa01be5a6149404adb82c0979a78f6347edd3ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74515
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
