# [H] phpseclib: guardrails needed on isPrime and randomPrime

## Summary
Severity: High
Advisory: GHSA-2528-jw5q-ww88
CVE: CVE-2024-27354
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-2528-jw5q-ww88
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=0.1.1 <1.0.23
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.47
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.36

## Details
### Impact
Anyone trying to generate a prime and testing the primality of a number.

### Patches
https://github.com/phpseclib/phpseclib/commit/ad5dbdf2129f5e0fb644637770b7f33de8ca8575

### Workarounds
Using the GMP extension would probably help, assuming that one has its own guardrails.

### Resources
https://github.com/phpseclib/phpseclib/commit/ad5dbdf2129f5e0fb644637770b7f33de8ca8575
https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-599-shi-bing.pdf

## References
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-2528-jw5q-ww88
- https://nvd.nist.gov/vuln/detail/CVE-2024-27354
- https://github.com/phpseclib/phpseclib/commit/2870c8fab3f132d2ed40a66c97a36fe5ab625698
- https://github.com/phpseclib/phpseclib/commit/ad5dbdf2129f5e0fb644637770b7f33de8ca8575
- https://github.com/phpseclib/phpseclib/commit/c55b75199ec8d12cec6eadf6da99da4a3712fe56
- https://gist.github.com/katzj/ee72f3c2a00590812b2ea3c0c8890e0b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpseclib/phpseclib/CVE-2024-27354.yaml
- https://github.com/phpseclib/phpseclib
- https://github.com/phpseclib/phpseclib/blob/master/phpseclib/Math/PrimeField.php#L49
- https://lists.debian.org/debian-lts-announce/2024/03/msg00002.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00003.html
