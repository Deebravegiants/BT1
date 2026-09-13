# [H] Automad has Broken Access Control: Unauthenticated exposure of administrator bcrypt password hashes and TOTP secrets via public API endpoint

## Summary
Severity: High
Advisory: GHSA-xm76-r88j-vm3g
CVE: CVE-2026-45332
CWE: CWE-200, CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-xm76-r88j-vm3g
Type: github-advisory

## Affected
- Packagist: `automad/automad` — affected >=2.0.0-alpha.1 <2.0.0-beta.28

## Details
### Summary

 A Broken Access Control vulnerability allows an unauthenticated attacker to retrieve the bcrypt password hash of every administrator account with a single POST request. The `/_api/user-collection/create-first-user` setup endpoint remains publicly accessible once initial configuration is complete and returns full serialized user data in the JSON response body.  

### Details

Affected version: 
 - bcrypt hash exposure: `>= 2.0.0-alpha.1, <= 2.0.0-beta.27`
 - TOTP secret exposure: only `2.0.0-beta.27`

### Impact

Any Automad installation reachable over HTTP is at risk no prior account, credentials, or special network position are required to exploit this vulnerability.

Potential impacts include:

- **Credential hash exposure enabling offline brute-force or dictionary attacks:** 
  bcrypt password hashes for every administrator are returned in a single unauthenticated response. While hashes are not plaintext passwords, the salt embedded in the hash is not secret it is visible in the response. Administrators using common or weak passwords are at direct risk of having their plaintext password recovered.
- **TOTP secret exposure:** 
  The TOTP secret is included in the response starting with version `2.0.0-beta.27`, the first release introducing TOTP-based two-factor authentication. If an attacker successfully recovers a plaintext password, two-factor authentication can be bypassed entirely. *Only version `2.0.0-beta.27` is affected by this specific issue.*  
- **Information disclosure:** 
  The response discloses the absolute filesystem path to the configuration directory. While the directory structure is publicly documented, the absolute server path may expose environment-specific information.

## Remediation

Update to version 2.0.0-beta.28 or later.

This issue was reported privately and fixed prior to public disclosure.

## References
- https://github.com/marcantondahmen/automad/security/advisories/GHSA-xm76-r88j-vm3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45332
- https://github.com/marcantondahmen/automad
