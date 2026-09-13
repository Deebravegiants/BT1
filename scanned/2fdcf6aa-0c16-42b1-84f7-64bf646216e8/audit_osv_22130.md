# [H] Out-of-bounds Read lead to application crashes or information leakage in ELF parsing.

## Summary
Severity: High
Advisory: CVE-2022-21711
Aliases: GHSA-jr8h-2657-m68r
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-01-24
Source: https://osv.dev/vulnerability/CVE-2022-21711
Type: osv

## Details
elfspirit is an ELF static analysis and injection framework that parses, manipulates, and camouflages ELF files. When analyzing the ELF file format in versions prior to 1.1, there is an out-of-bounds read bug, which can lead to application crashes or information leakage. By constructing a special format ELF file, the information of any address can be leaked. elfspirit version 1.1 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21711.json
- https://github.com/liyansong2018/elfspirit/security/advisories/GHSA-jr8h-2657-m68r
- https://nvd.nist.gov/vuln/detail/CVE-2022-21711
- https://github.com/liyansong2018/elfspirit/issues/1
- https://github.com/liyansong2018/elfspirit/commit/c5b0f5a9a24f2451bbeda4751d67633bc375e608
