# [M] zephyr: out-of-bound read in utf8_trunc

## Summary
Severity: Medium
Advisory: CVE-2024-6443
Aliases: GHSA-gg46-3rh2-v765
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-04
Source: https://osv.dev/vulnerability/CVE-2024-6443
Type: osv

## Details
In utf8_trunc in zephyr/lib/utils/utf8.c, last_byte_p can point to one byte before the string pointer if the string is empty.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6443.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-gg46-3rh2-v765
- https://nvd.nist.gov/vuln/detail/CVE-2024-6443
- https://github.com/zephyrproject-rtos/zephyr
