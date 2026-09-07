# [M] Appwrite Vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-5ffj-mph5-c5hv
CVE: CVE-2022-2925
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-10
Source: https://github.com/advisories/GHSA-5ffj-mph5-c5hv
Type: github-advisory

## Affected
- Packagist: `appwrite/server-ce` — affected >=0 <1.0.0-RC1

## Details
Appwrite is vulnerable to stored cross-site scripting in usernames, function names, storage bucket names, and database collection names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2925
- https://github.com/appwrite/appwrite/commit/b5b4d92623c13fa8e5c71736db461e81fb7a7ade
- https://drive.google.com/file/d/1JoMQy1KTodVtIVOzH3vKcC3AwZz0PrFb/view?usp=sharing
- https://github.com/appwrite/appwrite
- https://huntr.dev/bounties/a3b4148f-165f-4583-abed-5568696d99dc
