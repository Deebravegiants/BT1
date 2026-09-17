# [H] CVE-2020-22782

## Summary
Severity: High
Advisory: CVE-2020-22782
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2020-22782
Type: osv

## Details
Etherpad < 1.8.3 is affected by a denial of service in the import functionality. Upload of binary file to the import endpoint would crash the instance.

## References
- https://github.com/ether/etherpad-lite/issues/3825
