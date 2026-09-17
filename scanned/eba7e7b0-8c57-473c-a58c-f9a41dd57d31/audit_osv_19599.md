# [M] CVE-2021-22571

## Summary
Severity: Medium
Advisory: CVE-2021-22571
Aliases: GHSA-7fjx-657r-9r5h
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-18
Source: https://osv.dev/vulnerability/CVE-2021-22571
Type: osv

## Details
A local attacker could read files from some other users' SA360 reports stored in the /tmp folder during staging process before the files are loaded in BigQuery. We recommend upgrading to version 1.0.3 or above.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-7fjx-657r-9r5h
- https://github.com/google/sa360-webquery-bigquery/releases/tag/v1.0.3
- https://github.com/google/sa360-webquery-bigquery/pull/15
