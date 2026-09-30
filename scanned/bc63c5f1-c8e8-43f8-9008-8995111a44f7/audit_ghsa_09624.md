# [M] Nuclei: Environment variable disclosure via Response-Derived DSL Expressions

## Summary
Severity: Medium
Advisory: GHSA-jm34-66cf-qpvr
CVE: CVE-2026-41645
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-jm34-66cf-qpvr
Type: github-advisory

## Affected
- Go: `github.com/projectdiscovery/nuclei/v3` — affected >=3.0.0 <3.8.0

## Details
A vulnerability in Nuclei's expression evaluation engine makes it possible for a malicious target server to inject and execute supported DSL expressions. This happens when HTTP response data containing helper/function syntax gets reused by multi-step templates. If the `-env-vars` / `-ev` option is explicitly enabled, this can expose host environment variables. That option is off by default, so standard configurations are not affected by the information disclosure risk.

**Affected Component**

The issue lives in `expressions.Evaluate()` at `pkg/protocols/common/expressions/` and in the unresolved-variable validation path (`hasLiteralsOnly()`).

**Description**

`expressions.Evaluate()` replaces placeholders first, then scans the substituted output for expressions. Because of this two-pass approach, response-derived values (including extractor output and response body content) can be reinterpreted as DSL/helper syntax on the second pass.

When `-env-vars` (`-ev`) is enabled, environment variables get merged into the template variable map. A malicious target can return response data containing expressions like `{{env_var_name}}` which, when reused in a subsequent template request, resolve to actual environment variable values. This can expose sensitive host data like API keys, credentials, and tokens.

Without `-ev` enabled (the default), injected DSL expressions may still trigger helper functions such as `{{md5("test")}}`, but this has no meaningful security impact beyond unexpected behavior.

There is also a separate issue in `hasLiteralsOnly()`: it was evaluating helper expressions while deciding whether `{{...}}` contained unresolved variables, which caused validation logic to run side-effectful helpers even when the final request kept the value as a literal.

> [!NOTE]
The `-env-vars` / `-ev` option is off by default. Users who have not explicitly turned it on are not affected by the information disclosure aspect of this vulnerability.

**Affected Users**

- **CLI users** running multi-step templates (with extractors or flow-based request chaining) that reuse response-derived values against untrusted or attacker-controlled targets, with the `-ev` flag enabled.
- **SDK users** who have integrated Nuclei into platforms where `EnvironmentVariables` is set to `true` and scan targets are not fully trusted.

**Patches**

- The vulnerability is fixed in Nuclei v3.8.0. Upgrading to this version is strongly recommended.
- Relevant fix references: #7221, #7321.

**Mitigation**

Upgrade to Nuclei v3.8.0. The updated evaluation logic now collects expressions from the original template text before placeholder substitution and only evaluates those template-authored expressions.

If you have `-ev` enabled, disable it when scanning untrusted targets to avoid environment variable disclosure.

**Workarounds**

If upgrading is not an option right now, make sure `-env-vars` / `-ev` is not enabled when running multi-step templates against untrusted targets.

**Acknowledgments**

Nuclei thanks @gnuletik for reporting this issue through responsible disclosure via security@projectdiscovery.io

## References
- https://github.com/projectdiscovery/nuclei/security/advisories/GHSA-jm34-66cf-qpvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41645
- https://github.com/projectdiscovery/nuclei/pull/7221
- https://github.com/projectdiscovery/nuclei/pull/7321
- https://github.com/projectdiscovery/nuclei/commit/6c803c74d193f85f8a6d9803ce493fd302cad0eb
- https://github.com/projectdiscovery/nuclei/commit/d2217320162d5782ca7cb95bef9dda17063818f3
- https://github.com/projectdiscovery/nuclei
- https://github.com/projectdiscovery/nuclei/releases/tag/v3.8.0
