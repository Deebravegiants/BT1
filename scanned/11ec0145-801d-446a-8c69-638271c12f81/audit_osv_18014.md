# [H] CVE-2020-22785

## Summary
Severity: High
Advisory: CVE-2020-22785
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2020-22785
Type: osv

## Details
Etherpad < 1.8.3 is affected by a missing lock check which could cause a denial of service. Aggressively targeting random pad import endpoints with empty data would flatten all pads due to lack of rate limiting and missing ownership check.

## References
- https://github.com/ether/etherpad-lite/pull/3833
