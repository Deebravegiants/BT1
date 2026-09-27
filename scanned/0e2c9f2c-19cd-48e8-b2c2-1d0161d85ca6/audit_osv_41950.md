# [H] pds_core: fix error handling in pdsc_devcmd_wait

## Summary
Severity: High
Advisory: CVE-2026-64148
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64148
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

pds_core: fix error handling in pdsc_devcmd_wait

Fix two cases where pdsc_devcmd_wait() returns stale success from
the completion register instead of an error:

1. FW crash: If firmware stops running, the wait loop breaks early with
   running=false. The condition "if ((!done || timeout) && running)" is
   false, so error handling is bypassed and stale status is returned.
   Check !running first and return -ENXIO.

2. Timeout: If a command times out, err is set to -ETIMEDOUT but then
   overwritten by pdsc_err_to_errno(status) which reads stale status.
   Return -ETIMEDOUT immediately after cleaning up.

Both errors now propagate to pdsc_devcmd_locked() which queues
health_work for recovery.

## References
- https://git.kernel.org/stable/c/0e46b6635b03d29807f810c3b415c4755a3f958d
- https://git.kernel.org/stable/c/10ae3180095bbe2d378c5b1d6f2f2fd74dda3cc2
- https://git.kernel.org/stable/c/3231aff8ab26111c54e630b1a200fc43a729dd14
- https://git.kernel.org/stable/c/560d559324169fe0583d54c475b5329550a86f71
- https://git.kernel.org/stable/c/784dd2bdc622ed3cc6ef8e113aa1852e252de36f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
