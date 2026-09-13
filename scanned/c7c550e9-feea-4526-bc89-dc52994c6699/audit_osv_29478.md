# [M] CVE-2024-42698

## Summary
Severity: Medium
Advisory: CVE-2024-42698
CVSS: 4.3 (CVSS:3.1/AC:L/AV:N/A:N/C:N/I:L/PR:L/S:U/UI:N)
Published: 2024-08-28
Source: https://osv.dev/vulnerability/CVE-2024-42698
Type: osv

## Details
Roughly Enough Items (REI) v.16.0.729 and before contains an Improper Validation of Specified Index, Position, or Offset in Input vulnerability. The specific issue is a failure to validate slot index and decrement stack count in the Roughly Enough Items (REI) mod for Minecraft, which allows in-game item duplication.

## References
- https://gist.github.com/apple502j/7b1af0082449c9bfbf910e9a25ef3595
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42698.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42698
- https://github.com/shedaniel/RoughlyEnoughItems/commit/e80ca84f1affb91d2388ddb298bfc6b141828cad
