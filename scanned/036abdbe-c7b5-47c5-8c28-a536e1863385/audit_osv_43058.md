# [H] hwmon: (pmbus/core) honor vrm_version in pmbus_data2reg_vid()

## Summary
Severity: High
Advisory: CVE-2026-72397
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72397
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus/core) honor vrm_version in pmbus_data2reg_vid()

pmbus_data2reg_vid() hardcoded the VR11 encoding regardless of the
vrm_version configured by the driver, while pmbus_reg2data_vid()
already switched on it. Any driver that selects a non-VR11 VID mode
and exposes a regulator (or hwmon vout setter) sent dangerously
wrong codes to PMBUS_VOUT_COMMAND -- e.g. an nvidia195mv part asked
for 200 mV got the VR11 clamp to 500 mV encoded as 0xB2, which the
chip interprets as 1080 mV.

Mirror pmbus_reg2data_vid() so writes round-trip with reads.

## References
- https://git.kernel.org/stable/c/5bd0d47640395f8a8c34446b62d1781b88869dfa
- https://git.kernel.org/stable/c/828cd614e2af053ca5e1d6da767bbd8a1b5cabfb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
