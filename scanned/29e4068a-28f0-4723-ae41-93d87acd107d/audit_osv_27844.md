# [H] wifi: iwlwifi: fix a memory corruption

## Summary
Severity: High
Advisory: CVE-2024-26610
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-26610
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: fix a memory corruption

iwl_fw_ini_trigger_tlv::data is a pointer to a __le32, which means that
if we copy to iwl_fw_ini_trigger_tlv::data + offset while offset is in
bytes, we'll write past the buffer.

## References
- https://git.kernel.org/stable/c/05dd9facfb9a1e056752c0901c6e86416037d15a
- https://git.kernel.org/stable/c/870171899d75d43e3d14360f3a4850e90a9c289b
- https://git.kernel.org/stable/c/99a23462fe1a6f709f0fda3ebbe8b6b193ac75bd
- https://git.kernel.org/stable/c/aa2cc9363926991ba74411e3aa0a0ea82c1ffe32
- https://git.kernel.org/stable/c/cf4a0d840ecc72fcf16198d5e9c505ab7d5a5e4d
- https://git.kernel.org/stable/c/f32a81999d0b8e5ce60afb5f6a3dd7241c17dd67
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26610.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26610
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
