# [H] Hydra: hydra.utils.instantiate with untrusted config can lead to code execution

## Summary
Severity: High
Advisory: GHSA-2cp2-2r3c-7p7r
CVE: CVE-2026-68508
CWE: CWE-470, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-2cp2-2r3c-7p7r
Type: github-advisory

## Affected
- PyPI: `hydra-core` — affected >=0 <1.3.4

## Details
## Summary

`hydra.utils.instantiate()` resolves and calls Python objects from config. If an
application passes untrusted config to `instantiate()`, an attacker who controls
`_target_` and its arguments can cause arbitrary code execution in the consuming
process.

Hydra is not a network service. Exploitation requires a consuming application,
library, or user workflow to load attacker-controlled config, CLI overrides, or
model metadata and pass it to `hydra.utils.instantiate()`.

## Details

Hydra's instantiate API is designed to construct objects and call functions from
configuration. For example:

```yaml
component:
  _target_: package.module.Class
  arg: value
```

When this config is passed to `hydra.utils.instantiate()`, Hydra resolves
`_target_` and calls it with the provided arguments.

This is intended for trusted application configuration. However, if untrusted
input controls `_target_`, the config becomes a callable-selection mechanism. A
malicious config can select a callable capable of executing code or commands and
provide attacker-controlled arguments.

This issue is the same general class of problem discussed by Unit 42 for
downstream AI/ML libraries such as NVIDIA NeMo, where untrusted model metadata
was passed into Hydra instantiate:

https://unit42.paloaltonetworks.com/rce-vulnerabilities-in-ai-python-libraries/

Hydra 1.3.4 includes a blacklist for some dangerous `_target_` values. That
blacklist is defense-in-depth and is not a complete security boundary. The
blacklist is not present in the released `hydra-core` 1.3.3 package, so this
issue should not be described as a bypass of a released 1.3.3 blacklist.

## Impact

A successful attack can execute code in the process that calls
`hydra.utils.instantiate()`. The impact is limited to the privileges and
environment of that process.

Potential impact includes:

- Reading files, credentials, environment variables, or data accessible to the
  process
- Modifying files, outputs, checkpoints, or application state writable by the
  process
- Terminating or disrupting the process

## Affected Usage

Applications and libraries are affected when they pass untrusted or semi-trusted
config, model metadata, CLI overrides, or other externally controlled data to
`hydra.utils.instantiate()` without constraining which targets may be
instantiated.

Trusted application-owned configuration is not affected in the same way.

## Remediation

Hydra 1.3.4 hardens the existing behavior by adding a blacklist of obvious
dangerous targets. It is a substantial security improvement, and users remaining
on the 1.3 release line should upgrade to 1.3.4 or a newer version.

The unreleased Hydra 1.4 development line uses an allowlist-based instantiation
model that fully addresses this vulnerability class. The allowlist must come
from trusted application code or another trusted channel, not from the untrusted
config being instantiated.

Applications that consume untrusted or semi-trusted config should not pass it
directly to `hydra.utils.instantiate()`. They should validate `_target_` values
against a trusted allowlist before instantiation.

## References
- https://github.com/hydra-ecosystem/hydra/security/advisories/GHSA-2cp2-2r3c-7p7r
- https://github.com/hydra-ecosystem/hydra/issues/3259
- https://github.com/hydra-ecosystem/hydra/pull/3261
- https://github.com/hydra-ecosystem/hydra/commit/7faad0dcedfb4c0a364aa1067c0080fd6fdf8dca
- https://github.com/hydra-ecosystem/hydra
- https://github.com/hydra-ecosystem/hydra/releases/tag/v1.3.4
