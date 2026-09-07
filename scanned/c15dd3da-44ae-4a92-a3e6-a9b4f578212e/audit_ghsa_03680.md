# [C] Sensitive Data Exposure in pem

## Summary
Severity: Critical
Advisory: GHSA-pgcr-7wm4-mcv6
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-pgcr-7wm4-mcv6
Type: github-advisory

## Affected
- npm: `pem` — affected >=0 <1.13.2

## Details
Versions of `pem` before 1.13.2 expose sensitive data when the `readPkcs12` is used. 

The `readPkcs12` function reads the certificate and key data from a pkcs12 file using the encryption password. As part of this process it creates a globally readable file with a filename of 20 random 0-f characters in the temporary directory containing the password which is then read by OpenSSL. The file containing the password is never cleaned up after it is used giving access to the pkcs12 password to any other users with access to read files from the system.



## Recommendation

Update to version 1.13.2 or later.

## References
- https://github.com/Dexus/pem/pull/217
- https://github.com/Dexus/pem/commit/bed1190e4a08692ac903ae6043489f1f76bc67eb
- https://snyk.io/vuln/SNYK-JS-PEM-173687
- https://www.npmjs.com/advisories/723
