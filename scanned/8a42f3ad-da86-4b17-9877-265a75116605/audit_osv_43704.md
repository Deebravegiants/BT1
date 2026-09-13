# [H] ptp: ocp: Fix board ID over-read

## Summary
Severity: High
Advisory: CVE-2026-74603
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74603
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: ocp: Fix board ID over-read

The EEPROM board ID is a fixed 13-byte field and is not guaranteed to
contain a NUL terminator. Passing it directly to
devlink_info_version_fixed_put() treats it as a C string and may read
beyond the field.

Format at most OCP_BOARD_ID_LEN bytes into the existing local buffer
before reporting the ID. Use a precision limit because the snprintf()
output size alone does not bound the source string scan.

## References
- https://git.kernel.org/stable/c/3d965811be78473654e6e8cc8e4fb7b6b87aa6c1
- https://git.kernel.org/stable/c/5fd91dd4a143479b0575fb1f202ec1c501e71fd5
- https://git.kernel.org/stable/c/6b69f2ef10cdb018c0b127a7cab88e590bbddba4
- https://git.kernel.org/stable/c/72ef3ce80078199bfad32f98d055f44ba7cd0c3d
- https://git.kernel.org/stable/c/f8d7e5751267637190eff887c971d5b468106213
- https://git.kernel.org/stable/c/f92558bbe78d6284fedd053900f82a70f0aa8707
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74603.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74603
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
