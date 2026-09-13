# [H] CVE-2020-27174

## Summary
Severity: High
Advisory: CVE-2020-27174
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-27174
Type: osv

## Details
In Amazon AWS Firecracker before 0.21.3, and 0.22.x before 0.22.1, the serial console buffer can grow its memory usage without limit when data is sent to the standard input. This can result in a memory leak on the microVM emulation thread, possibly occupying more memory than intended on the host.

## References
- http://www.openwall.com/lists/oss-security/2020/10/23/1
- https://github.com/firecracker-microvm/firecracker/issues/2177
- https://github.com/firecracker-microvm/firecracker/pull/2178
- https://github.com/firecracker-microvm/firecracker/pull/2179
