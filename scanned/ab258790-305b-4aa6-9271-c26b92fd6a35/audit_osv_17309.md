# [M] CVE-2020-14423

## Summary
Severity: Medium
Advisory: CVE-2020-14423
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2020-14423
Type: osv

## Details
Convos before 4.20 does not properly generate a random secret in Core/Settings.pm and Util.pm. This leads to a predictable CONVOS_LOCAL_SECRET value, affecting password resets and invitations.

## References
- https://convos.chat/blog/2020/6/18/local-secret-got-more-secure
- https://github.com/Nordaaker/convos/commit/54d1763ac65c05aad27ad454b4e5a62ba8352d39
- https://github.com/Nordaaker/convos/compare/4.19...4.20
