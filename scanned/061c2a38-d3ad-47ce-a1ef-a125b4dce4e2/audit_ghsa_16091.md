# [M] UnoPim Stored XSS : Cookie hijacking through Create User function

## Summary
Severity: Medium
Advisory: GHSA-cgr4-c233-h733
CVE: CVE-2024-52305
CWE: CWE-616, CWE-692, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-cgr4-c233-h733
Type: github-advisory

## Affected
- Packagist: `unopim/unopim` — affected >=0 <0.1.5

## Details
### Summary
A vulnerability exists in the Create User process, allowing the creation of a new admin account with an option to upload a profile image. An attacker can upload a malicious SVG file containing an embedded script. When the profile image is accessed, the embedded script executes, leading to the potential theft of session cookies.

### Details
1. Login as admin
2. Go to Create User
3. Fill up everything in the registration form then upload SVG image as a profile picture
4. In SVG image, add script tag to prepare for XSS attack
5. Complete the Create User process
6. Right click at the image to obtain image URL address
7. XSS triggered
### PoC
The below link is a private YouTube video for PoC. 
https://youtu.be/5j8owD0--1A

### Impact
The stored XSS can lead to session hijacking and privilege escalation, effectively bypassing any CSRF protections in place.

## References
- https://github.com/unopim/unopim/security/advisories/GHSA-cgr4-c233-h733
- https://nvd.nist.gov/vuln/detail/CVE-2024-52305
- https://github.com/unopim/unopim/commit/9a0da7a0892c60f58df2351b5a9498dcb4cb8b7a
- https://github.com/unopim/unopim
