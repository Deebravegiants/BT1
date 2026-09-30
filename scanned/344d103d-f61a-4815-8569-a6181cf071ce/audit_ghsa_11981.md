# [H] AutoMapper Vulnerable to Denial of Service (DoS) via Uncontrolled Recursion

## Summary
Severity: High
Advisory: GHSA-rvv3-g6hj-g44x
CVE: CVE-2026-32933
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-rvv3-g6hj-g44x
Type: github-advisory

## Affected
- NuGet: `AutoMapper` — affected >=16.0.0 <16.1.1
- NuGet: `AutoMapper` — affected >=0 <15.1.1

## Details
### Summary

AutoMapper is vulnerable to a Denial of Service (DoS) attack. When mapping deeply nested object graphs, the library uses recursive method calls without enforcing a default maximum depth limit. This allows an attacker to provide a specially crafted object graph that exhausts the thread's stack memory, triggering a `StackOverflowException` and causing the entire application process to terminate.

### Description

The vulnerability exists in the core mapping engine. When a source object contains a property of the same type (or a type that eventually points back to itself), AutoMapper recursively attempts to map each level.

Because there is no default limit on how many levels deep this recursion can go, a sufficiently nested object (approximately 25,000+ levels in standard .NET environments) will exceed the stack size. Since `StackOverflowException` cannot be caught in modern .NET runtimes, the application cannot recover and will crash immediately.

### Impact

* **Availability:** An attacker can crash the application server, leading to a complete Denial of Service.
* **Process Termination:** Unlike standard exceptions, this terminates the entire process, not just the individual request thread.

### Proof of Concept (PoC)

The following C# code demonstrates the crash by creating a nested "Circular" object graph and attempting to map it:

```csharp
class Circular { public Circular Self { get; set; } }

// Setup configuration
var config = new MapperConfiguration(cfg => {
    cfg.CreateMap<Circular, Circular>();
});
var mapper = config.CreateMapper();

// Create a deeply nested object (28,000+ levels)
var root = new Circular();
var current = root;
for (int i = 0; i < 30000; i++) {
    current.Self = new Circular();
    current = current.Self;
}

// This call triggers the StackOverflowException and crashes the process
mapper.Map<Circular>(root);

```

### Recommended Mitigation

1. **Secure Defaults:** Implement a default `MaxDepth` (e.g., 32 or 64) for all mapping operations.
2. **Configurable Limit:** Allow users to increase this limit if necessary, but ensure it is enabled by default to protect unsuspecting developers.

## References
- https://github.com/LuckyPennySoftware/AutoMapper/security/advisories/GHSA-rvv3-g6hj-g44x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32933
- https://github.com/LuckyPennySoftware/AutoMapper/commit/0afaf1e91648fca1a57512e94dd00a76ee016816
- https://github.com/LuckyPennySoftware/AutoMapper
- https://github.com/LuckyPennySoftware/AutoMapper/discussions/4624
- https://github.com/LuckyPennySoftware/AutoMapper/releases/tag/v15.1.1
- https://github.com/LuckyPennySoftware/AutoMapper/releases/tag/v16.1.1
