# [M] jq: Missing runtime type checks for _strindices lead to crash and limited memory disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-39956
Aliases: GHSA-6gc3-3g9p-xx28
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-39956
Type: osv

## Details
jq is a command-line JSON processor. Prior to version 1.8.2, the _strindices builtin in jq's src/builtin.c passes its arguments directly to jv_string_indexes() without verifying they are strings, and jv_string_indexes() in src/jv.c relies solely on assert() checks that are stripped in release builds compiled with -DNDEBUG. This allows an attacker to crash jq trivially with input like _strindices(0), and by crafting a numeric value whose IEEE-754 bit pattern maps to a chosen pointer, achieve a controlled pointer dereference and limited memory read/probe primitive. Any deployment that evaluates untrusted jq filters against a release build is vulnerable. This issue has been patched in commit fdf8ef0f0810e3d365cdd5160de43db46f57ed03, which is part of version 1.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39956.json
- https://github.com/jqlang/jq/security/advisories/GHSA-6gc3-3g9p-xx28
- https://nvd.nist.gov/vuln/detail/CVE-2026-39956
- https://github.com/jqlang/jq/commit/fdf8ef0f0810e3d365cdd5160de43db46f57ed03
