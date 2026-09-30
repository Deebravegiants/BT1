# [M] PhoenixCart Vulnerable to Account Deletion Without Password Confirmation

## Summary
Severity: Medium
Advisory: CVE-2025-47272
Aliases: GHSA-62qj-pvwm-h8cv
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2025-47272
Type: osv

## Details
The CE Phoenix eCommerce platform, starting in version 1.0.9.7 and prior to version 1.1.0.3, allowed logged-in users to delete their accounts without requiring password re-authentication. An attacker with temporary access to an authenticated session (e.g., on a shared/public machine) could permanently delete the user’s account without knowledge of the password. This bypass of re-authentication puts users at risk of account loss and data disruption. Version 1.1.0.3 contains a patch for the issue.

## References
- https://github.com/CE-PhoenixCart/PhoenixCart/security/advisories/GHSA-62qj-pvwm-h8cv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47272.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47272
- https://github.com/CE-PhoenixCart/PhoenixCart/commit/e87162b15d31c4126acfc1aad6108e5b9955bb76
