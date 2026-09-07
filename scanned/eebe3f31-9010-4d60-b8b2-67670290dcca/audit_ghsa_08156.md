# [M] time vulnerable to stack exhaustion Denial of Service attack

## Summary
Severity: Medium
Advisory: GHSA-r6v5-fh4h-64xc
CVE: CVE-2026-25727
CWE: CWE-121
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-r6v5-fh4h-64xc
Type: github-advisory

## Affected
- crates.io: `time` — affected >=0.3.6 <0.3.47

## Details
### Impact

When user-provided input is provided to any type that parses with the RFC 2822 format, a denial of service attack via stack exhaustion is possible. The attack relies on formally deprecated and rarely-used features that are part of the RFC 2822 format used in a malicious manner. Ordinary, non-malicious input will never encounter this scenario.

### Patches

A limit to the depth of recursion was added in v0.3.47. From this version, an error will be returned rather than exhausting the stack.

### Workarounds

Limiting the length of user input is the simplest way to avoid stack exhaustion, as the amount of the stack consumed would be at most a factor of the length of the input.

Alternatively, avoiding the format altogether would also ensure that the vulnerability is not encountered. To do this, add

```toml
disallowed-types = ["time::format_description::well_known::Rfc2822"]
```

to your `clippy.toml` file. This will trigger the `clippy::disallowed_types` lint, which is warn-by-default and can be explicitly denied.

## References
- https://github.com/time-rs/time/security/advisories/GHSA-r6v5-fh4h-64xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25727
- https://github.com/time-rs/time/commit/1c63dc7985b8fa26bd8c689423cc56b7a03841ee
- https://github.com/time-rs/time
- https://github.com/time-rs/time/blob/main/CHANGELOG.md#0347-2026-02-05
- https://github.com/time-rs/time/releases/tag/v0.3.47
- https://rustsec.org/advisories/RUSTSEC-2026-0009.html
