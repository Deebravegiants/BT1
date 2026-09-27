# [M] CVE-2025-70100

## Summary
Severity: Medium
Advisory: CVE-2025-70100
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2025-70100
Type: osv

## Details
A divide-by-zero vulnerability in the ext4_block_set_lb_size function in src/ext4_blockdev.c of the lwext4 1.0.0 library allows attackers to cause a denial of service by providing a malformed ext4 filesystem image that results in a zero logical block size. The vulnerability is triggered during mount or image processing and leads to a Floating-Point Exception (FPE) under sanitizers or a runtime crash in standard builds due to missing validation of lb_size.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/5
- https://github.com/sigdevel/pocs/blob/main/res/lwext4/2/sig8_2_lwext4_ext4_blockdev_c_127
- https://infosec.exchange/@sigdevel/116668952003072580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70100.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70100
- https://github.com/gkostka/lwext4/issues/90
