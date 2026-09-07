# [H] Formwork improperly validates input of User role preventing site and panel availability

## Summary
Severity: High
Advisory: GHSA-c85w-x26q-ch87
CWE: CWE-1285, CWE-248
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2025-03-01
Source: https://github.com/advisories/GHSA-c85w-x26q-ch87
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=2.0.0-beta.1 <2.0.0-beta.4

## Details
### Summary
Improper validation of select fields allows attackers to craft an input that crashes the system, resulting in a 500 status and making the entire site and administration panel unavailable.
This clearly impacts the Availability aspect of the CIA triad (confidentiality, integrity, and availability), although the attack still has certain limitations.

### Details
The attack involves injecting any invalid user role value. Doing this will change the users data in a way that prevents users and then the entire site from loading. Even though the actual data change is minimal, the error is unrecoverable until a valid role parameter is restored by direct modification of the user account file.
Proper validation of select fields will prevent extraneous valid from being accepted and making the entire site and administration panel unavailable.

### Patches
- [**Formwork 2.x** (d9f0c1f)](https://github.com/getformwork/formwork/commit/d9f0c1feb3b9855d5bdc8bb189c0aaab2792e7ca) adds proper validation to select fields.

### Impact
The condition for this attack is having high privileges or Admin access, which means it could be exploited by an Insider Threat. Alternatively, if an attacker gains access to a privileged user account, they can execute the attack as well.
Overall, the attack is relatively difficult to carry out, but if successful, the impact and damage would be significant.

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-c85w-x26q-ch87
- https://github.com/getformwork/formwork/commit/d9f0c1feb3b9855d5bdc8bb189c0aaab2792e7ca
- https://github.com/getformwork/formwork
