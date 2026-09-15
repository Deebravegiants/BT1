# [M] Heap-based Buffer Overflow in radareorg/radare2

## Summary
Severity: Medium
Advisory: CVE-2022-1383
CVSS: 4.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-04-17
Source: https://osv.dev/vulnerability/CVE-2022-1383
Type: osv

## Details
Heap-based Buffer Overflow in GitHub repository radareorg/radare2 prior to 5.6.8. The bug causes the program reads data past the end of the intented buffer. Typically, this can allow attackers to read sensitive information from other memory locations or cause a crash.

## References
- https://huntr.dev/bounties/02b4b563-b946-4343-9092-38d1c5cd60c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1383.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1383
- https://github.com/radareorg/radare2/commit/1dd65336f0f0c351d6ea853efcf73cf9c0030862
