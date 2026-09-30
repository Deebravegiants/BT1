# [M] CVE-2021-44886

## Summary
Severity: Medium
Advisory: CVE-2021-44886
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-44886
Type: osv

## Details
In Zammad 5.0.2, agents can configure "out of office" periods and substitute persons. If the substitute persons didn't have the same permissions as the original agent, they could receive ticket notifications for tickets that they have no access to.

## References
- https://zammad.com/en/advisories/zaa-2021-21
