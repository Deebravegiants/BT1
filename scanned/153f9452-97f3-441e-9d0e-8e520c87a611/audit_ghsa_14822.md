# [M] Moodle HTTP authorization header is preserved between "emulated redirects"

## Summary
Severity: Medium
Advisory: GHSA-p2cj-86v4-7782
CVE: CVE-2024-38275
CWE: CWE-226, CWE-459
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-18
Source: https://github.com/advisories/GHSA-p2cj-86v4-7782
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.1
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.5
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.8
- Packagist: `moodle/moodle` — affected >=0 <4.1.11

## Details
The cURL wrapper in Moodle retained the original request headers when following redirects, so HTTP authorization header information could be unintentionally sent in requests to redirect URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38275
- https://github.com/moodle/moodle/commit/0df3c5837a592e6663c4d531ff6a1f776bc2f785
- https://github.com/moodle/moodle/commit/3e38c84315a7991ce5ef5f241f5e873b5ca24f01
- https://github.com/moodle/moodle/commit/836b2c23a210317d130017d77bb64e3b510869a9
- https://github.com/moodle/moodle/commit/f7988538b2208c55f2c40ce4f0815901dc88049b
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=459500
