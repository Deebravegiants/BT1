# [H] HID: core: Mitigate potential OOB by removing bogus memset()

## Summary
Severity: High
Advisory: CVE-2026-43048
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43048
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: Mitigate potential OOB by removing bogus memset()

The memset() in hid_report_raw_event() has the good intention of
clearing out bogus data by zeroing the area from the end of the incoming
data string to the assumed end of the buffer.  However, as we have
previously seen, doing so can easily result in OOB reads and writes in
the subsequent thread of execution.

The current suggestion from one of the HID maintainers is to remove the
memset() and simply return if the incoming event buffer size is not
large enough to fill the associated report.

Suggested-by Benjamin Tissoires <bentiss@kernel.org>

[bentiss: changed the return value]

## References
- https://git.kernel.org/stable/c/0a3fe972a7cb1404f693d6f1711f32bc1d244b1c
- https://git.kernel.org/stable/c/8f71034649738fdeb6859b8d6cddf132024fac06
- https://git.kernel.org/stable/c/bd6e1d0230cca9575f5d118148f51e2a56b5373f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43048.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
