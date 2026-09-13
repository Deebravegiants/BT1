# [H] ksmbd: transport_ipc: validate payload size before reading handle

## Summary
Severity: High
Advisory: CVE-2025-40084
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-29
Source: https://osv.dev/vulnerability/CVE-2025-40084
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.158, >=6.2.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: transport_ipc: validate payload size before reading handle

handle_response() dereferences the payload as a 4-byte handle without
verifying that the declared payload size is at least 4 bytes. A malformed
or truncated message from ksmbd.mountd can lead to a 4-byte read past the
declared payload size. Validate the size before dereferencing.

This is a minimal fix to guard the initial handle read.

## References
- https://git.kernel.org/stable/c/2dc125f5da134c0915a840b62565c60a595673dd
- https://git.kernel.org/stable/c/6f40e50ceb99fc8ef37e5c56e2ec1d162733fef0
- https://git.kernel.org/stable/c/867ffd9d67285612da3f0498ca618297f8e41f01
- https://git.kernel.org/stable/c/898d527ed94c19980a4d848f10057f1fed578ffb
- https://git.kernel.org/stable/c/a02e432d5130da4c723aabe1205bac805889fdb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40084.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
