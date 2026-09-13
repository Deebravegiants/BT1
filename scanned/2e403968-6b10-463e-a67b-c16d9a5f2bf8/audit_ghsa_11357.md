# [C] `@orpc/client` has Prototype Pollution via `StandardRPCJsonSerializer` Deserialization

## Summary
Severity: Critical
Advisory: GHSA-m272-9rp6-32mc
CVE: CVE-2026-28794
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-m272-9rp6-32mc
Type: github-advisory

## Affected
- npm: `@orpc/client` — affected >=0 <1.13.6

## Details
### Summary
A critical Prototype Pollution vulnerability exists in the RPC JSON deserializer of the `@orpc/client` package. The vulnerability allows unauthenticated, remote attackers to inject arbitrary properties into the global `Object.prototype`. Because this pollution persists for the lifetime of the Node.js process and affects all objects, it can lead to severe security breaches, including authentication bypass, denial of service, and potentially Remote Code Execution.

### Vulnerability Details
The root cause lies in the `deserialize()` method of `StandardRPCJsonSerializer`. When processing attacker-controlled path segments from the `meta` and `maps` arrays, the deserializer fails to implement validation or sanitization for dangerous JavaScript object keys, specifically `__proto__` and `constructor`:

https://github.com/middleapi/orpc/blob/819ed2e0897b18a5d6a4ca85ba68568f055004a1/packages/client/src/adapters/standard/rpc-json-serializer.ts#L137-L213

There are two primary distinct write vectors available to an attacker:

1. The `meta` vector: Writes type-constrained values (e.g., `Map`, `Set`, `Date`) to arbitrary object paths.
2. The `maps` vector: Allows the injection of arbitrary string values. This occurs because the return value of `getBlob(i)` (which relies on `FormData.get(i.toString())`) is cast `as Blob`. Since this is strictly a TypeScript compile-time cast, the runtime execution allows standard text fields to return as arbitrary strings.

Crucially, this deserialization process occurs at the very beginning of the request lifecycle before any Zod schema validation takes place. Consequently, a malicious payload will successfully pollute the prototype even if the request is subsequently rejected by the validation layer.

This issue impacts all server adapters utilizing the RPC protocol.

### Proof of Concept
To reproduce the vulnerability, set up the [playgrounds/astro](https://github.com/middleapi/orpc/tree/main/playgrounds/astro) environment and start the development server using `pnpm dev`. 

Run the following `curl` command to send a crafted payload:

```bash
curl -X POST http://localhost:4321/rpc/planet/create \
     -F 'data={"json":{},"meta":[],"maps":[["__proto__","role"]]}' \
     -F '0=admin'
```

Result: The deserializer evaluates `maps`, follows the `__proto__` path, and maps index `0` to the string `"admin"`. This immediately applies `Object.prototype.role = "admin"` across the entire Node.js server instance. 

### Impact
Servers relying on `StandardRPCJsonSerializer` for deserialization are immediately susceptible to global prototype pollution. The potential impacts including:

- Privilege Escalation / Authorization Bypass: Attackers can bypass flawed security checks. For example, if the server relies on a defaulted property check like `if (user.role === "admin")`, the application will evaluate this as `true` for all users globally.
- Remote Code Execution: If the application or its dependencies contain susceptible prototype pollution gadgets (e.g., dynamically executing shell commands or scripts based on object properties), this vulnerability can be leveraged into full RCE.
- Denial of Service: Attackers can overwrite built-in methods (e.g., `toString`) or set objects into unexpected states, causing the application to crash or throw unhandled exceptions globally.

## References
- https://github.com/middleapi/orpc/security/advisories/GHSA-m272-9rp6-32mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-28794
- https://github.com/middleapi/orpc/commit/1dba06fc6f938c2486de303c2fa096bc1c8418b5
- https://github.com/middleapi/orpc
