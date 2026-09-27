# [M] CVE-2021-46434

## Summary
Severity: Medium
Advisory: CVE-2021-46434
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-03-28
Source: https://osv.dev/vulnerability/CVE-2021-46434
Type: osv

## Details
EMQ X Dashboard V3.0.0 is affected by username enumeration in the "/api /v3/auth" interface. When a user login, the application returns different results depending on whether the account is correct, that allowed an attacker to determine if a given username was valid

## References
- https://github.com/emqx/emqx/issues/6791
