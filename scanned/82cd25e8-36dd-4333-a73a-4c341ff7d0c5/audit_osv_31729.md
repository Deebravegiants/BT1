# [M] scsi: storvsc: Ratelimit warning logs to prevent VM denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-21690
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2025-21690
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.15.178, >=5.16.0 <6.1.128, >=6.2.0 <6.6.75, >=6.7.0 <6.12.12, >=6.13.0 <6.13.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: storvsc: Ratelimit warning logs to prevent VM denial of service

If there's a persistent error in the hypervisor, the SCSI warning for
failed I/O can flood the kernel log and max out CPU utilization,
preventing troubleshooting from the VM side. Ratelimit the warning so
it doesn't DoS the VM.

## References
- https://git.kernel.org/stable/c/01d1ebdab9ccb73c952e1666a8a80abd194dbc55
- https://git.kernel.org/stable/c/088bde862f8d3d0fc52e40e66a0484a246837087
- https://git.kernel.org/stable/c/182a4b7c731e95c08cb47f14b87a272b6ab2b2da
- https://git.kernel.org/stable/c/81d4dd05c412ba04f9f6b85b718e6da833be290c
- https://git.kernel.org/stable/c/d0f0af1bafef33b3e2aa8c3a4ef44db48df9b0ea
- https://git.kernel.org/stable/c/d2138eab8cde61e0e6f62d0713e45202e8457d6d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21690.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21690
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
