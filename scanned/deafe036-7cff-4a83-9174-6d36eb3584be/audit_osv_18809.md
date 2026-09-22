# [M] CVE-2020-36316

## Summary
Severity: Medium
Advisory: CVE-2020-36316
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2020-36316
Type: osv

## Details
In RELIC before 2021-04-03, there is a buffer overflow in PKCS#1 v1.5 signature verification because garbage bytes can be present.

## References
- https://github.com/relic-toolkit/relic/
- https://github.com/relic-toolkit/relic/tree/32eb4c257fc80328061d66639b1cdb35dbed51a2
- https://github.com/relic-toolkit/relic/commit/76c9a1fdf19d9e92e566a77376673e522aae9f80
- https://github.com/relic-toolkit/relic/issues/155
