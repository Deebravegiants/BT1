# [H] Weak password hash in LiveHelperChat

## Summary
Severity: High
Advisory: GHSA-vx8v-g3p3-88vg
CVE: CVE-2022-1235
CWE: CWE-916
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-vx8v-g3p3-88vg
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <3.96

## Details
The secrethash, which the application relies for multiple security measures, can be brute-forced. The hash is quite small, with only 10 characters of only hexadecimal, making 16^10 possilibities ( 1.099.511.627.776 ). The SHA1 of the secret can be obtained via a captcha string and brute-forced offline with an GPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1235
- https://github.com/livehelperchat/livehelperchat/commit/6538d6df3d8a60fee254170b08dd76a161f7bfdc
- https://github.com/livehelperchat/livehelperchat
- https://huntr.dev/bounties/92f7b2d4-fa88-4c62-a2ee-721eebe01705
