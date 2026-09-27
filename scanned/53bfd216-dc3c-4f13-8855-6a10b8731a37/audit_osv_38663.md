# [C] jq: Signed-int overflow in `stack_reallocate` (jq VM stack)

## Summary
Severity: Critical
Advisory: CVE-2026-41257
Aliases: GHSA-4jm8-m363-4539
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-41257
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, the jq bytecode VM's data stack tracks its allocation size in a signed int. When the stack grows beyond ≈1 GiB (via deeply nested generator forks), the doubling arithmetic overflows. The wrapped value is passed to realloc and then used for a memmove with attacker-influenced offsets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41257.json
- https://github.com/jqlang/jq/security/advisories/GHSA-4jm8-m363-4539
- https://nvd.nist.gov/vuln/detail/CVE-2026-41257
