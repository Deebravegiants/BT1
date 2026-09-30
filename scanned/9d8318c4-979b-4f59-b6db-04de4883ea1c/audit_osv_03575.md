# [H] ALPINE-CVE-2026-32316

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-32316
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32316
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. An integer overflow vulnerability exists through version 1.8.1 within the jvp_string_append() and jvp_string_copy_replace_bad functions, where concatenating strings with a combined length exceeding 2^31 bytes causes a 32-bit unsigned integer overflow in the buffer allocation size calculation, resulting in a drastically undersized heap buffer. Subsequent memory copy operations then write the full string data into this undersized buffer, causing a heap buffer overflow classified as CWE-190 (Integer Overflow) leading to CWE-122 (Heap-based Buffer Overflow). Any system evaluating untrusted jq queries is affected, as an attacker can crash the process or potentially achieve further exploitation through heap corruption by crafting queries that produce extremely large strings. The root cause is the absence of string size bounds checking, unlike arrays and objects which already have size limits. The issue has been addressed in commit e47e56d226519635768e6aab2f38f0ab037c09e5.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32316
