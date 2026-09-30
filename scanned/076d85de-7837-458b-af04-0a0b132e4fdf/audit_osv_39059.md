# [H] accel/ivpu: Disallow re-exporting imported GEM objects

## Summary
Severity: High
Advisory: CVE-2026-43498
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-21
Source: https://osv.dev/vulnerability/CVE-2026-43498
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Disallow re-exporting imported GEM objects

Prevent re-exporting of imported GEM buffers by adding a custom
prime_handle_to_fd callback that checks if the object is imported
and returns -EOPNOTSUPP if so.

Re-exporting imported GEM buffers causes loss of buffer flags settings,
leading to incorrect device access and data corruption.

## References
- https://git.kernel.org/stable/c/3756043dd695bba34cc728cdc5688dcb49ac8043
- https://git.kernel.org/stable/c/7dd57d7a6350770dfc283287125c409e995200e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43498.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43498
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
