# [M] Crypt_GPG does not prevent additional options in GPG calls

## Summary
Severity: Medium
Advisory: GHSA-59x4-67mh-px54
CVE: CVE-2022-24953
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-18
Source: https://github.com/advisories/GHSA-59x4-67mh-px54
Type: github-advisory

## Affected
- Packagist: `pear/crypt_gpg` — affected >=0 <1.6.7

## Details
The Crypt_GPG extension before 1.6.7 for PHP does not prevent additional options in GPG calls, which presents a risk for certain environments and GPG versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24953
- https://github.com/pear/Crypt_GPG/commit/29c0fbe96d0d4063ecd5c9a4644cb65a7fb7cc4e
- https://github.com/pear/Crypt_GPG/commit/74c8f989cefbe0887274b461dc56197e121bfd04
- https://github.com/pear/Crypt_GPG
