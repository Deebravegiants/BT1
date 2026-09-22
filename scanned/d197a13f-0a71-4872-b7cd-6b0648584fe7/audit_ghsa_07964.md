# [M] CI4MS Vulnerable to User Email Enumeration via Password Reset Flow

## Summary
Severity: Medium
Advisory: GHSA-654x-9q7r-g966
CVE: CVE-2026-25509
CWE: CWE-203, CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-654x-9q7r-g966
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.28.5.0

## Details
**Summary**

The authentication implementation in CI4MS is vulnerable to email enumeration. An unauthenticated attacker can determine whether an email address is registered in the system by analyzing the application's response during the password reset process.

**Vulnerability Details**

- The password reset flow returns different responses based on whether the provided email address exists in the database or not.
- If the email is registered, the system typically returns a success message (e.g., "Password reset link has been sent").

If the email is not registered, the system returns an error message (e.g., "User not found" or a different HTTP status code).

This discrepancy allows attackers to programmatically "enumerate" or confirm valid user emails, which can then be used for targeted phishing attacks or brute-force attempts.

**Steps to Reproduce**

1. Navigate to the password reset page of the CI4MS installation.
2. Enter an email address that you know is not registered (e.g., nonexistent@example.com) and submit. Note the response message/code.
3. Enter an email address that is registered (e.g., an admin or test account) and submit. Note the different response.
4. The difference between these two responses confirms the enumeration vulnerability.

**Suggested Mitigation**

Implement a uniform, generic response for all password reset requests, regardless of whether the email exists. Recommended message: "If an account is associated with this email address, a password reset link has been sent."

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-654x-9q7r-g966
- https://nvd.nist.gov/vuln/detail/CVE-2026-25509
- https://github.com/ci4-cms-erp/ci4ms/commit/86be2930d1c54eb7575102563302b2f3bafcb653
- https://github.com/ci4-cms-erp/ci4ms
