# [C] ksmbd: fix use-after-free in smb2_open during durable reconnect

## Summary
Severity: Critical
Advisory: CVE-2026-53010
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53010
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in smb2_open during durable reconnect

In smb2_open, the call to ksmbd_put_durable_fd(fp) drops the reference
to the durable file descriptor early during the durable reconnect
process. If an error occurs subsequently (eg, ksmbd_iov_pin_rsp fails)
or a scavenger accesses the file, it leads to a use-after-free when
accessing fp properties (eg fp->create_time).

Move the single put to the end of the function below err_out2 so fp
stays valid until smb2_open returns.

## References
- https://git.kernel.org/stable/c/1baff47b81f94f9231c91236aa511420d0e266b9
- https://git.kernel.org/stable/c/97a0cd55283b4e63fd92804da91c8d9896adcad9
- https://git.kernel.org/stable/c/ce2e164c1c51c3f7813b80f8c926836e896bcbb3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53010.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53010
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
