# [H] HID: core: Fix OOB read in hid_get_report for numbered reports

## Summary
Severity: High
Advisory: CVE-2026-80604
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80604
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: Fix OOB read in hid_get_report for numbered reports

When a caller passes a size of 0 to hid_report_raw_event() for a
numbered report, the function originally called hid_get_report() before
performing any size validation.

Inside hid_get_report(), if the report is numbered (report_enum->numbered
is true), it unconditionally dereferences data[0] to extract the report ID.
With a size of 0, this results in an out-of-bounds read or kernel panic.

Fix this by moving the numbered report size validation check before the
call to hid_get_report(), ensuring that size is at least 1 before
dereferencing the data pointer.

## References
- https://git.kernel.org/stable/c/30ff978af92cb51c9ba99f96fc4f4ac80d7001ba
- https://git.kernel.org/stable/c/af1a9b65ebe8a948eda805c14b78d4d0767cb1b5
- https://git.kernel.org/stable/c/c1fc0d3aff26ec9ff885b3e4c92eba98cf349678
- https://git.kernel.org/stable/c/c39f5765ad840b71ff8db812d0210f216cca96e4
- https://git.kernel.org/stable/c/c973d53bcd420b58c4a34c68198746286d77e9fa
- https://git.kernel.org/stable/c/dd395744e4ed87956fcbf81ecc6a20c51e35fa4e
- https://git.kernel.org/stable/c/f7e8117e42b20c30d2a5edab82c944a5e381d791
- https://git.kernel.org/stable/c/f8896b684e246f3f00f45ba2b6803ae59b9cc768
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80604
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
