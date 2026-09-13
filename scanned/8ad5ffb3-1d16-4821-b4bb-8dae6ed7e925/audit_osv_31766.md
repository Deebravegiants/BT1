# [H] usbnet: ipheth: fix DPE OoB read

## Summary
Severity: High
Advisory: CVE-2025-21741
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21741
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: ipheth: fix DPE OoB read

Fix an out-of-bounds DPE read, limit the number of processed DPEs to
the amount that fits into the fixed-size NDP16 header.

## References
- https://git.kernel.org/stable/c/22475242ddb70e35c9148234be9a3aa9fb8efff9
- https://git.kernel.org/stable/c/5835bf66c50ac2b85ed28b282c2456c3516ef0a6
- https://git.kernel.org/stable/c/971b8c572559e52d32a2b82f2d9e0685439a0117
- https://git.kernel.org/stable/c/ee591f2b281721171896117f9946fced31441418
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21741.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21741
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
