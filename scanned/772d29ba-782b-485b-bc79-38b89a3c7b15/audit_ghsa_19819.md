# [M] Manifest Uses a One-Way Hash without a Salt

## Summary
Severity: Medium
Advisory: GHSA-h8h6-7752-g28c
CVE: CVE-2025-27408
CWE: CWE-759
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-h8h6-7752-g28c
Type: github-advisory

## Affected
- npm: `manifest` — affected >=0 <4.9.2

## Details
### Summary
Manifest employs a weak password hashing implementation that uses SHA3 without a salt. This exposes user passwords to a higher risk of being cracked if an attacker gains access to the database. Without the use of a salt, identical passwords across multiple users will result in the same hash, making it easier for attackers to identify and exploit patterns, thereby accelerating the cracking process.

### Details
Analysis of the application source code reveals that user passwords are hashed using the SHA3 algorithm without implementing a unique salt per user.
```
const newUser: AuthenticableEntity = entityRepository.create(signupUserDto)
newUser.password = SHA3(newUser.password).toString()
```
This approach results in deterministic password hashes, which can be identified by comparing the hashes for users with matching credentials.

![password without salt](https://github.com/user-attachments/assets/8ce816ab-0351-44d4-9aa3-717266441d6e)


### PoC
1. Create two users with the same password (it could be admin or any other authenticatable entity)
2. Extract their password hashes from the database
3. Verify that both hashes are identical, confirming the absence of unique salts

### Impact
This is a cryptographic weakness vulnerability that affects all users of the system. The lack of a unique salt when hashing passwords reduces protection against database breaches, as attackers who gain access to the database can more efficiently crack user passwords. Since identical passwords result in identical hashes, attackers can use precomputed hash databases (e.g., Rainbow Tables) or offline brute-force attacks to reverse the hashes and obtain user passwords, increasing the risk of compromised accounts and further system exploitation.

## References
- https://github.com/mnfst/manifest/security/advisories/GHSA-h8h6-7752-g28c
- https://nvd.nist.gov/vuln/detail/CVE-2025-27408
- https://github.com/mnfst/manifest/commit/3ed6f1324e96ad469ad929d470dcd0cc386c6c69
- https://github.com/mnfst/manifest
