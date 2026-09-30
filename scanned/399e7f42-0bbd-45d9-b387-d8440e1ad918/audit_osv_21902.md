# [H] Heap buffer overflow in libr/bin/format/mach0/mach0.c in radareorg/radare2

## Summary
Severity: High
Advisory: CVE-2022-1240
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/CVE-2022-1240
Type: osv

## Details
Heap buffer overflow in libr/bin/format/mach0/mach0.c in GitHub repository radareorg/radare2 prior to 5.8.6. If address sanitizer is disabled during the compiling, the program should executes into the `r_str_ncpy` function. Therefore I think it is very likely to be exploitable. For more general description of heap buffer overflow, see [CWE](https://cwe.mitre.org/data/definitions/122.html).

## References
- https://huntr.dev/bounties/e589bd97-4c74-4e79-93b5-0951a281facc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1240.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1240
- https://github.com/radareorg/radare2/commit/ca8d8b39f3e34a4fd943270330b80f1148129de4
