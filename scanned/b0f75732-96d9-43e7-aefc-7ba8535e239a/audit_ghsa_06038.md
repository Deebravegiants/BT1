# [C] kobako Sandbox Escape: guest eval reaches host RCE via method_missing → public_send (any bound Service)

## Summary
Severity: Critical
Advisory: GHSA-7pwq-q9jf-539h
CVE: CVE-2026-55107
CWE: CWE-470, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-7pwq-q9jf-539h
Type: github-advisory

## Affected
- RubyGems: `kobako` — affected >=0.1.0 <0.9.1

## Details
### Summary
A guest mruby script running inside the Kobako sandbox can execute arbitrary
Ruby in the host process, fully escaping the sandbox.

### Details
A host embeds bound "Service" objects that guest scripts call across the wasm
boundary through the transport dispatcher. The dispatcher passed the
guest-supplied method name straight to `Object#public_send` on the bound
object, with no restriction to the object's own methods:

```ruby
target.public_send(method.to_sym, *args, **kwargs, &block)
```

`public_send` can invoke any public method, including Ruby's ambient
reflection surface. A guest pivots through the public `send` into otherwise
private Kernel methods: a dispatch request with `method = "send"` and
`args = [:eval, "<ruby>"]` evaluates to `target.send(:eval, "<ruby>")`,
running attacker-controlled Ruby in the host. Any bound Service object is
sufficient — no Service-specific behavior is required.

### Proof of Concept
A guest call equivalent to:

```
Service.send(:eval, "<arbitrary host ruby>")
```

executes in the host process and can read or modify host state, spawn
processes, and so on.

### Impact
Complete sandbox escape leading to remote code execution in the host process,
defeating the gem's central guarantee of isolating untrusted mruby scripts.
Any deployment that runs untrusted or attacker-influenced scripts is affected.
All released versions (0.1.0 through 0.9.0) are vulnerable; the dispatcher
carried the same unguarded `public_send` sink under three successive names
(`registry` → `rpc` → `transport`).

### Patches
Fixed in 0.9.1. The dispatcher now rejects any method whose resolved owner is
a core/meta module (`BasicObject`, `Kernel`, `Object`, `Module`, `Class`), so
only methods the bound object itself defines — or dynamically handles via
`method_missing` — remain reachable. The ambient reflection methods (`send`,
`__send__`, `public_send`, `instance_eval`, `instance_exec`, `method`,
`instance_variable_get`, …) are all owned by those modules and are blocked.

### Workarounds
None within the affected versions. Until you can upgrade, do not bind any
host Service object into a sandbox that runs untrusted scripts. Upgrade to
0.9.1.

### References
- GHSA-7pwq-q9jf-539h
- Fix commit: 64f8470

### Credits
Reported and fixed by Ahmed Al Hafoudh.

## References
- https://github.com/elct9620/kobako/security/advisories/GHSA-7pwq-q9jf-539h
- https://github.com/elct9620/kobako/commit/64f84700c81f44902bed9211318d5362f44987b3
- https://github.com/elct9620/kobako
