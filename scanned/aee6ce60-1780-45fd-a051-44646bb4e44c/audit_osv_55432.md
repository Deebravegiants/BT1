# [M] CVE-2025-47229

## Summary
Severity: Medium
Advisory: CVE-2025-47229
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-03
Source: https://osv.dev/vulnerability/CVE-2025-47229
Type: osv

## Details
libpspp-core.a in GNU PSPP through 2.0.1 allows attackers to cause a denial of service (var_set_leave_quiet assertion failure and application exit) via crafted input data, such as data that triggers a call from src/data/dictionary.c code into src/data/variable.c code.

## References
- https://savannah.gnu.org/bugs/?67049
