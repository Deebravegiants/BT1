# [M] TSPortal's Uncontrolled User Creation via Validation Side Effects Leads to Potential Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-f346-8rp3-4h9h
CVE: CVE-2026-33541
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-f346-8rp3-4h9h
Type: github-advisory

## Affected
- Packagist: `miraheze/ts-portal` — affected >=0 <34

## Details
### Summary
A flaw in TSPortal allowed attackers to create arbitrary user records in the database by abusing validation logic. While validation correctly rejected invalid usernames, a side effect within a validation rule caused user records to be created regardless of whether the request succeeded. This could be exploited to cause uncontrolled database growth, leading to a potential denial of service (DoS).

### Details
When submitting a Data Processing Agreement (DPA) request in TSPortal, the `DPAAlreadyLive` validation rule previously called `User::findOrCreate()`.

This method created a user record if one did not already exist.

Although username validation (via `MirahezeUsernameRule`) correctly rejected invalid usernames, the `DPAAlreadyLive` rule was still executed during validation. Because it performed a state-changing operation, it created user records even when the overall validation failed and no DPA was created.

As a result:
- Validation correctly rejected invalid input
- However, user records were still inserted into the database as a side effect

These records were created:
- Without a successful DPA request
- Without audit logging tied to a completed action
- Without visibility into their origin

### Impact
An attacker could exploit this behavior by automating requests with invalid usernames, resulting in:

- Mass creation of arbitrary user records
- Unbounded database growth
- Increased storage and indexing overhead
- Potential degradation of application performance

At scale, this could lead to a denial of service condition due to resource exhaustion.

### Proof of Concept
1. Submit a DPA request using an invalid username
2. Ensure the request fails validation due to `MirahezeUsernameRule`
3. Observe that a corresponding user record is still created in the database

This behavior was confirmed prior to remediation.

### Root Cause
The issue stemmed from:
- Performing state-changing operations (`findOrCreate`) inside validation logic
- Validation rules executing regardless of overall validation success
- Lack of separation between validation and persistence layers

### Mitigation
The issue has been fixed by removing database write operations from validation logic.

Specifically:
- Replaced `User::findOrCreate()` with a non-mutating lookup (`User::firstWhere(...)`)
- Ensured validation rules only perform read operations
- Prevented user creation unless all validation passes

## References
- https://github.com/miraheze/TSPortal/security/advisories/GHSA-f346-8rp3-4h9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33541
- https://github.com/miraheze/TSPortal
- https://issue-tracker.miraheze.org/T15115
