# [M] Element Android PIN autologout bypass

## Summary
Severity: Medium
Advisory: CVE-2025-27606
Aliases: GHSA-632v-9pm3-m8ch
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-03-14
Source: https://osv.dev/vulnerability/CVE-2025-27606
Type: osv

## Details
Element Android is an Android Matrix Client provided by Element. Element Android up to version 1.6.32 can, under certain circumstances, fail to logout the user if they input the wrong PIN more than the configured amount of times. An attacker with physical access to a device can exploit this to guess the PIN. Version 1.6.34 solves the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27606.json
- https://github.com/element-hq/element-android/security/advisories/GHSA-632v-9pm3-m8ch
- https://nvd.nist.gov/vuln/detail/CVE-2025-27606
- https://github.com/element-hq/element-android/commit/53bd78b05de375c6e6b0b5aa794a56b4ba95984c
- https://github.com/element-hq/element-android/commit/87d7fcdc8036a4db4da8c403f87c73a64a546304
