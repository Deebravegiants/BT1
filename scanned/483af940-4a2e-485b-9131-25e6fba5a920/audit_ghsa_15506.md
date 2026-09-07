# [M]  starcitizentools/citizen-skin vulnerable to stored, self-XSS in the "real name" field

## Summary
Severity: Medium
Advisory: GHSA-62r2-gcxr-426x
CVE: CVE-2024-47536
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-30
Source: https://github.com/advisories/GHSA-62r2-gcxr-426x
Type: github-advisory

## Affected
- Packagist: `starcitizentools/citizen-skin` — affected >=2.6.3 <2.31.0

## Details
### Summary
A user with the `editmyprivateinfo` right or who can otherwise change their name can XSS themselves by setting their "real name" to an XSS payload.

### Details
Here's the offending line:
https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/d45c3d69f30863f622f16eb40dd41d3ca943454a/includes/Components/CitizenComponentUserInfo.php#L137

This was introduced in 717d16af35b10dab04d434aefddbf991fc8c168c

### PoC
1. Login
2. Go to Special:Preferences
3. Set the real name field to a string like `<script>alert("Admin with a propensity for self-XSSes")</script>`
4. Save your settings and use Citizen if it's not being used already

![](https://github.com/user-attachments/assets/22adbb70-fcd7-4f81-8e53-1f5f3a730270)

### Impact
Any user who can change their name (whether it's through the editmyprivateinfo right or through other means) can add XSS payloads that trigger for themselves only.

## References
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/security/advisories/GHSA-62r2-gcxr-426x
- https://nvd.nist.gov/vuln/detail/CVE-2024-47536
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/717d16af35b10dab04d434aefddbf991fc8c168c
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/commit/86da3e07718c8d8da6f4310386fef85599606f9b
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen
- https://github.com/StarCitizenTools/mediawiki-skins-Citizen/blob/d45c3d69f30863f622f16eb40dd41d3ca943454a/includes/Components/CitizenComponentUserInfo.php#L137
