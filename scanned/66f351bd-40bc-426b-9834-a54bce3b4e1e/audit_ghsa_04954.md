# [M] nono-py's policy JSON accepts unknown security fields

## Summary
Severity: Medium
Advisory: GHSA-m8j6-rc5x-wv36
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-m8j6-rc5x-wv36
Type: github-advisory

## Affected
- PyPI: `nono-py` — affected >=0 <0.10.1

## Details
### Summary

nono-py policy handling could fail open in two ways. First, resolving a policy-derived `ProxyConfig` did not automatically enforce `CapabilitySet.proxy_only`, allowing sandboxed children to bypass a resolved domain allowlist by using direct network access. Second, policy JSON accepted unknown security-sensitive fields, so misspelled or unsupported restrictions could be silently ignored.

### Impact

A sandboxed child may receive broader network access than the policy author intended. This can allow outbound requests outside the configured proxy allowlist and may expose sensitive data depending on the execution environment and workload.

### Older-kernel note

On Linux kernels without Landlock ABI v4 network rules, patched versions continue to support proxy-only enforcement through the seccomp supervisor fallback introduced in 807fb4b. Users on older kernels should ensure policy-resolved proxy configurations are coupled to `CapabilitySet.proxy_only(proxy);` merely injecting proxy environment variables is not sufficient.

## References
- https://github.com/always-further/nono-py/security/advisories/GHSA-m8j6-rc5x-wv36
- https://github.com/nolabs-ai/nono-py/commit/2897ee20df0d75afd298d94840b9d135b3b3a6e9
- https://github.com/nolabs-ai/nono-py/commit/807fb4bce2385b9e88185bf160e0792b588813c7
- https://github.com/always-further/nono-py
