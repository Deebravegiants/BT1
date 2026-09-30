# [C] e107 Second-Order Code Execution via eval()-Based Deserialization in e_array::unserialize()

## Summary
Severity: Critical
Advisory: CVE-2026-57859
Aliases: GHSA-568x-w5qj-vr7c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-57859
Type: osv

## Details
e107 prior to version 2.3.8 contains a code execution vulnerability in the e_array deserialization handler that allows an attacker with out-of-band database write access to execute arbitrary PHP code by storing a crafted payload in the user_prefs column. The e_array::unserialize() function in e107_handlers/core_functions.php performs only a prefix check for the string 'array' before passing the stored value to eval(), causing automatic PHP execution whenever the affected user's preferences are materialized through e_user_pref::load().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57859.json
- https://github.com/e107inc/e107/security/advisories/GHSA-568x-w5qj-vr7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-57859
- https://www.vulncheck.com/advisories/e107-second-order-code-execution-via-eval-based-deserialization-in-e-array-unserialize
- https://github.com/e107inc/e107/commit/40e73cefde85b32e1227dfac9956a5cb87046277
- https://github.com/e107inc/e107
