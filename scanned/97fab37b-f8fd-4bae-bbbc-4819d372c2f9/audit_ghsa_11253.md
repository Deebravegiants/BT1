# [M] Parse Server vulnerable to schema poisoning via prototype pollution in deep copy

## Summary
Severity: Medium
Advisory: GHSA-9ccr-fpp6-78qf
CVE: CVE-2026-32878
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-9ccr-fpp6-78qf
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.20
- npm: `parse-server` — affected >=0 <8.6.44

## Details
### Impact

An attacker can bypass the default request keyword denylist protection and the class-level permission for adding fields by sending a crafted request that exploits prototype pollution in the deep copy mechanism. This allows injecting fields into class schemas that have field addition locked down, and can cause permanent schema type conflicts that cannot be resolved even with the master key.

### Patches

The vulnerable third-party deep copy library has been replaced with a built-in deep clone mechanism that handles prototype properties safely, allowing the existing denylist check to correctly detect and reject the prohibited keyword.

### Workarounds

None.

### Vulnerability Independence

This vulnerability is not caused by or dependent on a vulnerability in a third-party dependency.

The third-party `deepcopy` library that was replaced in the fix has no known CVE or security advisory regarding this. The library functions as designed. It is not vulnerable.

The vulnerability is in parse-server's own request processing logic. Parse-server's security-critical keyword denylist check runs after the deep copy step in the request pipeline. The deep copy step strips `__proto__` properties as a normal part of its cloning behavior, which means the denylist check never sees the prohibited key. This allows an attacker to bypass both the denylist protection and class-level permissions for adding fields, resulting in schema poisoning.

The root cause is parse-server's reliance on a cloning mechanism that alters the shape of the data before the security check can inspect it. This is a logic flaw in parse-server's security pipeline, not a vulnerability in a dependency. Replacing the cloning mechanism was the fix for parse-server's own bug.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-9ccr-fpp6-78qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-32878
- https://github.com/parse-community/parse-server/pull/10200
- https://github.com/parse-community/parse-server/pull/10201
- https://github.com/parse-community/parse-server
