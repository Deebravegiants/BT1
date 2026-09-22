# [M] Mass Assignment in Preset Creation Allows User ID Manipulation in danny-avila/librechat

## Summary
Severity: Medium
Advisory: CVE-2024-10359
CVSS: 4.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10359
Type: osv

## Details
In danny-avila/librechat version v0.7.5-rc2, a vulnerability exists in the preset creation functionality where a user can manipulate the user ID field through mass assignment. This allows an attacker to inject a different user ID into the preset object, causing the preset to appear in the UI of another user. The vulnerability arises because the backend saves the entire object received without validating the attributes and their values, impacting both integrity and confidentiality.

## References
- https://huntr.com/bounties/bba65eb4-4c83-4f33-83c1-ede5ed0d5656
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10359.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10359
- https://github.com/danny-avila/librechat/commit/e3e52402f69accc35c6d0acd9c3266ae1cb6333f
