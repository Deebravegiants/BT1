# [M] Insufficient Entropy in PHPServerMon PRNG

## Summary
Severity: Medium
Advisory: GHSA-97w9-gcc7-vr8g
CVE: CVE-2021-4240
CWE: CWE-1241, CWE-330, CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-97w9-gcc7-vr8g
Type: github-advisory

## Affected
- Packagist: `phpservermon/phpservermon` — affected >=0 <3.6.0

## Details
A vulnerability, which was classified as problematic, was found in phpservermon. This affects the function `generatePasswordResetToken` of the file `src/psm/Service/User.php`. The manipulation leads to use of predictable algorithm in random number generator. The exploit has been disclosed to the public and may be used. The name of the patch is 3daa804d5f56c55b3ae13bfac368bb84ec632193. It is recommended to apply a patch to fix this issue. The identifier VDB-213717 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4240
- https://github.com/phpservermon/phpservermon/commit/3daa804d5f56c55b3ae13bfac368bb84ec632193
- https://github.com/phpservermon/phpservermon
- https://huntr.dev/bounties/2-phpservermon/phpservermon
- https://vuldb.com/?id.213717
