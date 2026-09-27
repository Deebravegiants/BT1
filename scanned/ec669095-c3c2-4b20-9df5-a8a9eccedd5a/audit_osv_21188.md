# [M] CVE-2021-41123

## Summary
Severity: Medium
Advisory: CVE-2021-41123
Aliases: GHSA-6c7j-7jf3-9p3j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/CVE-2021-41123
Type: osv

## Details
Survey Solutions is a survey management and data collection system. In affected versions the Headquarters application publishes /metrics endpoint available to any user. None of the survey answers are ever exposed, only the aggregate counters, including count of interviews, or count of assignments. Starting from version 21.09.1 the endpoint is turned off by default.

## References
- https://github.com/surveysolutions/surveysolutions/security/advisories/GHSA-6c7j-7jf3-9p3j
- https://github.com/surveysolutions/surveysolutions/commit/99e7e8345cb98f2eda08e37976e3d3aeb49971c9
