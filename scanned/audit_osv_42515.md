# [H] hwmon: occ: validate poll response sensor blocks

## Summary
Severity: High
Advisory: CVE-2026-68340
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68340
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: occ: validate poll response sensor blocks

The OCC poll response parser walks a counted list of sensor data blocks.
It used the static backing-array capacity as the parse boundary, but a
transport response makes only data_length bytes current and valid. A
truncated response can therefore make the parser consume a block header or
block extent outside the current response.

Use data_length as the parent boundary, prove the fixed poll header and
each current block header before reading them, and prove the complete block
before advancing. Keep parsed sensor metadata local until the complete
response has passed validation, then publish it. Propagate
malformed-response errors before publishing the OCC as active.

## References
- https://git.kernel.org/stable/c/112525534ab5cff482d35897ca4ca11fd3a76f46
- https://git.kernel.org/stable/c/1902e9572901d37901e3db1f3f6b0885f4e49a66
- https://git.kernel.org/stable/c/538d862cc0dbd5c732fe26d5aad98eae039e6676
- https://git.kernel.org/stable/c/54cb78eceb4e286ccd5a5c01a4632157860d47f0
- https://git.kernel.org/stable/c/6e6c72c37433640514db325408bd6913ad28fe69
- https://git.kernel.org/stable/c/70e76e700fc6c46afb4e17aec099a1ea089b4a22
- https://git.kernel.org/stable/c/b042e538e98b939fccfffc464e2c34c29f0e96ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68340.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
