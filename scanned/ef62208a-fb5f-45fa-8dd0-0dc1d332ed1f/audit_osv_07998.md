# [C] CVE-2016-1000005

## Summary
Severity: Critical
Advisory: CVE-2016-1000005
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2016-1000005
Type: osv

## Details
mcrypt_get_block_size did not enforce that the provided "module" parameter was a string, leading to type confusion if other types of data were passed in. This issue affects HHVM versions prior to 3.9.5, all versions between 3.10.0 and 3.12.3 (inclusive), and all versions between 3.13.0 and 3.14.1 (inclusive).

## References
- https://www.facebook.com/security/advisories/cve-2016-1000005
- https://github.com/facebook/hhvm/commit/39e7e177473350b3a5c34e8824af3b98e25efa89
