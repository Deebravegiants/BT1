# [H] Lightning Flow Scanner Vulnerable to Code Injection via Unsafe Use of `new Function()` in APIVersion Rule

## Summary
Severity: High
Chain: lightning-flow-scanner
Component: lightning-flow-scanner
CVE: CVE-2025-67750
CWE: Improper Control of Generation of Code ('Code Injection')
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-55jh-84jv-8mx8
Type: github-advisory

## Details
### Impact
The APIVersion rule uses `new Function()` to evaluate expression strings. A malicious crafted flow metadata file can cause arbitrary JavaScript execution during scanning. An attacker could execute arbitrary JavaScript during a scan by supplying a malicious expression within rule configuration or crafted flow metadata. This could compromise developer machines, CI runners, or editor environments.

### Patches
The patch removes all uses of `new Function()` and replaces them with a safer parser. It now validates operators (`>`, >=`, `<`, `<=`, `==`) and performs numeric comparisons without evaluating untrusted JavaScript.

**version:** core-v6.10.6,
**version vsx:**: v2.4.4
**version app:**: v3.1.0

### Work around

```
// --- Handle APIVersion rule separately to avoid unsafe-eval in the core library ---
      const apiVersionConfig = ruleConfig.rules.APIVersion;
      if (apiVersionConfig) {
        delete ruleConfig.rules.APIVersion;
      }

// Manually evaluate the APIVersion rule, if it was configured.
      if (apiVersionConfig) {
        const flowApiVer = this.currentFlow.apiVersion || this.currentFlow.xmlData?.apiVersion;
        const apiVersionRuleDef = allRules.find(r => r.name === "APIVersion");

        // Determine the required expression (e.g. ">=58").
        let requiredExpr;
        if (apiVersionConfig.expression) {
          requiredExpr = apiVersionConfig.expression;
        } else if (apiVersionConfig.threshold != null) {
          requiredExpr = `>=${apiVersionConfig.threshold}`;
        }

        if (requiredExpr) {
          const minVer = parseInt(requiredExpr.replace(/[^0-9]/g, ""), 10);
          const operator = requiredExpr.replace(/[0-9]/g, "").trim();
          const operators = {
            ">=": (a, b) => a < b,
            "<": (a, b) => a >= b,
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-55jh-84jv-8mx8_
