# [H] CVE-2021-25923

## Summary
Severity: High
Advisory: CVE-2021-25923
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-25923
Type: osv

## Details
In OpenEMR, versions 5.0.0 to 6.0.0.1 are vulnerable to weak password requirements as it does not enforce a maximum password length limit. If a malicious user is aware of the first 72 characters of the victim user’s password, he can leverage it to an account takeover.

## References
- https://github.com/openemr/openemr/commit/28ca5c008d4a408b60001a67dfd3e0915f9181e0
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25923
