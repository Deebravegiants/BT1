# [H] Users enumeration allowed through Rest API in Combodo iTop

## Summary
Severity: High
Advisory: CVE-2024-51739
Aliases: GHSA-2hmf-p27w-phf9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-51739
Type: osv

## Details
Combodo iTop is a simple, web based IT Service Management tool. Unauthenticated user can perform users enumeration, which can make it easier to bruteforce a valid account. As a fix the sentence displayed after resetting password no longer shows if the user exists or not. This fix is included in versions 2.7.11, 3.0.5, 3.1.2, and 3.2.0. Users are advised to upgrade. Users unable to upgrade may overload the dictionary entry `"UI:ResetPwd-Error-WrongLogin"` through an extension and replace it with a generic message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51739.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-2hmf-p27w-phf9
- https://nvd.nist.gov/vuln/detail/CVE-2024-51739
