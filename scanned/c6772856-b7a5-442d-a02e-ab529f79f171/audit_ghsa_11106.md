# [M] Serialize JavaScript has CPU Exhaustion Denial of Service via crafted array-like objects

## Summary
Severity: Medium
Advisory: GHSA-qj8w-gfj5-8c6v
CVE: CVE-2026-34043
CWE: CWE-400, CWE-834
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-qj8w-gfj5-8c6v
Type: github-advisory

## Affected
- npm: `serialize-javascript` — affected >=5.0.0 <7.0.5

## Details
### Impact

**What kind of vulnerability is it?**

It is a **Denial of Service (DoS)** vulnerability caused by CPU exhaustion. When serializing a specially crafted "array-like" object (an object that inherits from `Array.prototype` but has a very large `length` property), the process enters an intensive loop that consumes 100% CPU and hangs indefinitely.

**Who is impacted?**

Applications that use `serialize-javascript` to serialize untrusted or user-controlled objects are at risk. While direct exploitation is difficult, it becomes a high-priority threat if the application is also vulnerable to **Prototype Pollution** or handles untrusted data via **YAML Deserialization**, as these could be used to inject the malicious object.

### Patches

**Has the problem been patched?**

Yes, the issue has been patched by replacing `instanceof Array` checks with `Array.isArray()` and using `Object.keys()` for sparse array detection.

**What versions should users upgrade to?**

Users should upgrade to **`v7.0.5`** or later.

### Workarounds

**Is there a way for users to fix or remediate the vulnerability without upgrading?**

There is no direct code-level workaround within the library itself. However, users can mitigate the risk by:

* Validating and sanitizing all input before passing it to the `serialize()` function.
* Ensuring the environment is protected against Prototype Pollution.
* Upgrading to **`v7.0.5`** as soon as possible.

### Acknowledgements

Serialize JavaScript thanks **Tomer Aberbach** (@TomerAberbach) for discovering and privately disclosing this issue.

## References
- https://github.com/yahoo/serialize-javascript/security/advisories/GHSA-qj8w-gfj5-8c6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34043
- https://github.com/yahoo/serialize-javascript/commit/f147e90269b58bb6e539cfdf3d0e20d6ad14204b
- https://github.com/yahoo/serialize-javascript
- https://github.com/yahoo/serialize-javascript/releases/tag/v5.0.0
- https://github.com/yahoo/serialize-javascript/releases/tag/v7.0.5
