# [H] md/raid5: validate payload size before accessing journal metadata

## Summary
Severity: High
Advisory: CVE-2026-46070
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46070
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid5: validate payload size before accessing journal metadata

r5c_recovery_analyze_meta_block() and
r5l_recovery_verify_data_checksum_for_mb() iterate over payloads in a
journal metadata block using on-disk payload size fields without
validating them against the remaining space in the metadata block.

A corrupted journal contains payload sizes extending beyond the PAGE_SIZE
boundary can cause out-of-bounds reads when accessing payload fields or
computing offsets.

Add bounds validation for each payload type to ensure the full payload
fits within meta_size before processing.

## References
- https://git.kernel.org/stable/c/28d3ff7109c66e99dc1b7cddacb5c760849620ef
- https://git.kernel.org/stable/c/33698bd1b2db9764a29df7751533d33967ff5c98
- https://git.kernel.org/stable/c/406aa86394ead347c47428fb51b6359bdaa2257d
- https://git.kernel.org/stable/c/73ce72edd113374801045924d4417199963f73a3
- https://git.kernel.org/stable/c/b0cc3ae97e893bf54bbce447f4e9fd2e0b88bff9
- https://git.kernel.org/stable/c/c3a1cf78bd1bbb51b2cc5189b4743056553c1e0e
- https://git.kernel.org/stable/c/c96c6f01d84b5c67db1bf1cc8591c0b7146826fc
- https://git.kernel.org/stable/c/ef4851d8324fd978ca1ff9ec76a275438f887743
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46070.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
