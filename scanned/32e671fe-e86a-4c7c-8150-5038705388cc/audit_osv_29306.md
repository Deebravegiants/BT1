# [M] CVE-2024-41565

## Summary
Severity: Medium
Advisory: CVE-2024-41565
CVSS: 4.3 (CVSS:3.1/AC:L/AV:N/A:N/C:N/I:L/PR:L/S:U/UI:N)
Published: 2024-08-28
Source: https://osv.dev/vulnerability/CVE-2024-41565
Type: osv

## Details
JustEnoughItems (JEI) 19.5.0.33 and before contains an Improper Validation of Specified Index, Position, or Offset in Input vulnerability. The specific issue is a failure to validate slot index in JEI for Minecraft, which allows in-game item duplication.

## References
- https://gist.github.com/apple502j/05123abb1d1c89c31afde15a9b34e2ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41565.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41565
- https://github.com/mezz/JustEnoughItems/commit/99ff43ba1009c44c6d935e2ab8a6c9292bb12873
