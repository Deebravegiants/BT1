# [M] NCalc: Denial of Service via Unbounded and Non-Terminating Factorial Evaluation

## Summary
Severity: Medium
Advisory: GHSA-3w5p-95mh-gq75
CVE: CVE-2026-55254
CWE: CWE-190, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-3w5p-95mh-gq75
Type: github-advisory

## Affected
- NuGet: `NCalc.Core` — affected >=0 <6.1.1
- NuGet: `NCalcSync` — affected >=0 <6.1.1

## Details
### Impact

A denial-of-service (DoS) vulnerability exists in the factorial operator implementation of NCalc. Specially crafted expressions containing extremely large factorial operands can trigger excessive CPU consumption or cause evaluation to enter a non-terminating loop due to integer overflow in the factorial calculation logic.

Applications that evaluate untrusted expressions using affected versions of NCalc may be vulnerable to resource exhaustion, potentially resulting in service disruption or application unresponsiveness.

This issue can be triggered with expressions such as:

```text
99999999999999!
9223372036854775807!
1.5e16!
```

### Patches

The vulnerability has been fixed by adding bounds validation for factorial operands and rejecting unsupported values before evaluation.

Users should upgrade to the first release containing the fix from pull request #575. (**v6.1.1+**)

### Workarounds

If upgrading is not immediately possible:

* Do not evaluate expressions originating from untrusted users.
* Validate or sanitize expressions before evaluation and reject factorial operations on large values.
* Implement execution time limits, request timeouts, or cancellation mechanisms around expression evaluation.

These mitigations may reduce exposure but do not fully address the underlying vulnerability.

## References
- https://github.com/ncalc/ncalc/security/advisories/GHSA-3w5p-95mh-gq75
- https://github.com/ncalc/ncalc/pull/575
- https://github.com/ncalc/ncalc
