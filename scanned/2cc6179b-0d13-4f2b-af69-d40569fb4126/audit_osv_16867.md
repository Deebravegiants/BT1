# [M] CVE-2020-10102

## Summary
Severity: Medium
Advisory: CVE-2020-10102
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10102
Type: osv

## Details
An issue was discovered in Zammad 3.0 through 3.2. The Forgot Password functionality is implemented in a way that would enable an anonymous user to guess valid user emails. In the current implementation, the application responds differently depending on whether the input supplied was recognized as associated with a valid user. This behavior could be used as part of a two-stage automated attack. During the first stage, an attacker would iterate through a list of account names to determine which correspond to valid accounts. During the second stage, the attacker would use a list of common passwords to attempt to brute force credentials for accounts that were recognized by the system in the first stage.

## References
- https://zammad.com/news/security-advisory-zaa-2020-07
