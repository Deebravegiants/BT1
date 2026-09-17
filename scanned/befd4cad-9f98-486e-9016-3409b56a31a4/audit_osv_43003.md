# [H] ASoC: SOF: ipc4-control: Validate notification payload size

## Summary
Severity: High
Advisory: CVE-2026-72303
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72303
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc4-control: Validate notification payload size

Validate MODULE_NOTIFICATION payload length before reading
bytes/channel data in control update handling.

## References
- https://git.kernel.org/stable/c/5bdfeccb7fbf6e000fc783cd8412732e67c1ad0c
- https://git.kernel.org/stable/c/c29f5b4498894aebb2f87b1a29bb320e2f9348f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72303.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
