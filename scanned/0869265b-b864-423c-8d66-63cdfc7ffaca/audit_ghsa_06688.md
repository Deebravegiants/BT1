# [C] seroval: `seroval.fromJSON()` Promise resolver type confusion invokes attacker-controlled methods during deserialization

## Summary
Severity: Critical
Advisory: GHSA-mv8w-475r-vwqw
CVE: CVE-2026-59940
CWE: CWE-502, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-mv8w-475r-vwqw
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0 <1.5.3

## Details
## Summary

A type confusion issue in `seroval.fromJSON()` allowed attacker-controlled JSON input to cause Promise control nodes to operate on values from the general deserialization reference table without first verifying that those values were genuine internal promise resolver records.

In applications that deserialize untrusted Seroval JSON with plugins enabled, this could allow attacker-controlled deserialization side effects. In downstream server frameworks that register plugins returning callable wrappers, this primitive could become unintended server-side invocation and, depending on exposed application functionality, remote code execution or equivalent server compromise.

The issue was fixed in `seroval@1.5.3`.

## Affected package

- Package: `seroval`
- Affected API: `fromJSON()`
- Affected versions: versions prior to `1.5.3` that contain the vulnerable Promise resolver reference handling
- Patched version: `1.5.3`

## Impact

The vulnerable deserialization path could confuse attacker-created values in the general reference table with Seroval's internal promise resolver records.

Direct impact in `seroval` is a deserialization side-effect primitive when untrusted JSON is deserialized with plugins enabled. Downstream impact depends on registered plugins and framework usage. If a downstream framework registers plugins that deserialize sensitive callable wrappers, attacker-controlled input may be able to trigger unintended server-side invocation during deserialization.

A concrete downstream impact scenario was validated privately against TanStack Start before the `1.5.3` fix. With `seroval@1.5.3`, the downstream reproducer no longer succeeds.

## Remediation

Upgrade to `seroval@1.5.3` or later.

Downstream projects that accept Seroval JSON from untrusted clients should also consider defense-in-depth controls:

- restrict accepted Seroval node types for client-to-server payloads;
- allowlist plugin tags for inbound deserialization;
- avoid registering plugins that produce callable or privileged values for untrusted inputs unless strictly necessary;
- add regression tests ensuring deserialization cannot cause unintended server-side invocation as a side effect.

## Fix verification

The original private reproducer was verified against `seroval@1.5.2` and no longer reproduces against `seroval@1.5.3`.

Validation results:

- `seroval@1.5.2`: vulnerable behavior reproduced.
- `seroval@1.5.3`: deserialization aborts before the attacker-controlled side effect occurs.
- TanStack Start downstream proof with `seroval@1.5.3`: no evidence side effect is produced.

## Credit

Reported by [Mufeed VH](https://x.com/mufeedvh) from [Winfunc Research](https://winfunc.com).

## Disclosure / coordination note

The downstream TanStack Start impact was coordinated privately. Technical exploit details and proof-of-concept reproduction material have been omitted from this advisory draft for discretion.

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-mv8w-475r-vwqw
- https://github.com/lxsmnsyc/seroval
- https://www.npmjs.com/package/seroval/v/1.5.3
