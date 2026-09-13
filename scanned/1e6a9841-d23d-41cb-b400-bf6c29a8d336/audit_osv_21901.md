# [H] Out-of-bounds Write in libr/bin/format/ne/ne.c in radareorg/radare2

## Summary
Severity: High
Advisory: CVE-2022-1238
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/CVE-2022-1238
Type: osv

## Details
Out-of-bounds Write in libr/bin/format/ne/ne.c in GitHub repository radareorg/radare2 prior to 5.6.8. This vulnerability is heap overflow and may be exploitable. For more general description of heap buffer overflow, see [CWE](https://cwe.mitre.org/data/definitions/122.html).

## References
- https://huntr.dev/bounties/47422cdf-aad2-4405-a6a1-6f63a3a93200
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1238.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1238
- https://github.com/radareorg/radare2/commit/c40a4f9862104ede15d0ba05ccbf805923070778
