# [H] parisc: Fix locking in pdc_iodc_print() firmware call

## Summary
Severity: High
Advisory: CVE-2022-50518
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2022-50518
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: Fix locking in pdc_iodc_print() firmware call

Utilize pdc_lock spinlock to protect parallel modifications of the
iodc_dbuf[] buffer, check length to prevent buffer overflow of
iodc_dbuf[], drop the iodc_retbuf[] buffer and fix some wrong
indentings.

## References
- https://git.kernel.org/stable/c/04a603058e70b8b881bb7860b8bd649f931f2591
- https://git.kernel.org/stable/c/553bc5890ed96a8d006224c3a4673c47fee0d12a
- https://git.kernel.org/stable/c/7236aae5f81f3efbd93d0601e74fc05994bc2580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50518.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50518
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
