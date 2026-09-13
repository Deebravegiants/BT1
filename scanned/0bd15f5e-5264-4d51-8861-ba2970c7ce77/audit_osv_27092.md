# [M] CVE-2024-10302

## Summary
Severity: Medium
Advisory: CVE-2024-10302
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2024-10302
Type: osv

## Details
The user self-signup flow in multiple WSO2 products fails to adequately validate user-supplied input. This weakness allows arbitrary unvalidated data to be included within user claims, which are then used by downstream processes.

Allowing unvalidated input into user claims can lead to various security risks. Malicious or malformed data injected during signup could be processed by other parts of the application, potentially enabling attacks such as content manipulation, redirection, user interface inconsistencies, unauthorized actions, and data exposure. The actual impact depends on how the compromised data is consumed and the privileges associated with the affected users.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2026/WSO2-2024-3740/
