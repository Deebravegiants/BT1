# [H] CVE-2020-29160

## Summary
Severity: High
Advisory: CVE-2020-29160
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-29160
Type: osv

## Details
An issue was discovered in Zammad before 3.5.1. A REST API call allows an attacker to change Ticket Article data in a way that defeats auditing.

## References
- https://zammad.com/en/advisories/zaa-2020-24
- https://github.com/zammad/zammad/commit/28944de180a88698509a656f61558bf9d7f810f4
