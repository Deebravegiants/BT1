# [H] platform/x86: intel: punit_ipc: fix memory corruption

## Summary
Severity: High
Advisory: CVE-2025-68303
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68303
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: intel: punit_ipc: fix memory corruption

This passes the address of the pointer "&punit_ipcdev" when the intent
was to pass the pointer itself "punit_ipcdev" (without the ampersand).
This means that the:

	complete(&ipcdev->cmd_complete);

in intel_punit_ioc() will write to a wrong memory address corrupting it.

## References
- https://git.kernel.org/stable/c/15d560cdf5b36c51fffec07ac2a983ab3bff4cb2
- https://git.kernel.org/stable/c/3e7442c5802146fd418ba3f68dcb9ca92b5cec83
- https://git.kernel.org/stable/c/46e9d6f54184573dae1dcbcf6685a572ba6f4480
- https://git.kernel.org/stable/c/9b9c0adbc3f8a524d291baccc9d0c04097fb4869
- https://git.kernel.org/stable/c/a21615a4ac6fecbb586d59fe2206b63501021789
- https://git.kernel.org/stable/c/c2ee6d38996775a19bfdf20cb01a9b8698cb0baa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68303.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
