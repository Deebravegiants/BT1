# [H] accel/amdxdna: Validate command buffer payload count

## Summary
Severity: High
Advisory: CVE-2026-23424
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23424
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Validate command buffer payload count

The count field in the command header is used to determine the valid
payload size. Verify that the valid payload does not exceed the remaining
buffer space.

## References
- https://git.kernel.org/stable/c/3464e751755172ddbb849c1bd92f5f59e95c59a1
- https://git.kernel.org/stable/c/3ed2ae6b3fe869f99b75afd02045ba5c0c0773e2
- https://git.kernel.org/stable/c/901ec3470994006bc8dd02399e16b675566c3416
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23424.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23424
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
