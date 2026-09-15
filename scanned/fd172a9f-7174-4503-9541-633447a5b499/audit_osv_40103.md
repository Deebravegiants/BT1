# [H] jq --rawfile invalid-state reuse after String too long causes heap-buffer-overflow

## Summary
Severity: High
Advisory: CVE-2026-49839
Aliases: GHSA-cfh2-vwfq-qfmm
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-49839
Type: osv

## Details
jq is a command-line JSON processor. Prior to 1.8.2,` jq --rawfile` can turn a handled oversized-string error into invalid-state reuse and a real heap out-of-bounds write in assertion-disabled builds. When jv_load_file(raw=1) reads an attacker-controlled file, it repeatedly appends file chunks to the same jv string accumulator. Once jv_string_append_buf() returns jv_invalid_with_msg("String too long"), the raw-file loop does not stop. If the file contains at least one more byte, the next loop iteration appends a new chunk to an object that is already invalid. With assertions enabled this aborts in jvp_string_ptr(). With assertions disabled, the invalid object is interpreted as a string object and ASan reports heap-buffer-overflow. This vulnerability is fixed in 1.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49839.json
- https://github.com/jqlang/jq/security/advisories/GHSA-cfh2-vwfq-qfmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-49839
