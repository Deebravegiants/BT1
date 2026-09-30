# [H] Keras is vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-36fq-jgmw-4r9c
CVE: CVE-2025-9906
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-36fq-jgmw-4r9c
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.11.0

## Details
### Arbitrary Code Execution in Keras

Keras versions prior to 3.11.0 allow for arbitrary code execution when loading a crafted `.keras` model archive, even when `safe_mode=True`.

The issue arises because the archive’s `config.json` is parsed before layer deserialization. This can invoke `keras.config.enable_unsafe_deserialization()`, effectively disabling safe mode from within the loading process itself. An attacker can place this call first in the archive and then include a `Lambda` layer whose function is deserialized from a pickle, leading to the execution of attacker-controlled Python code as soon as a victim loads the model file.

Exploitation requires a user to open an untrusted model; no additional privileges are needed. The fix in version 3.11.0 enforces safe-mode semantics *before* reading any user-controlled configuration and prevents the toggling of unsafe deserialization via the config file.

**Affected versions:** < 3.11.0
**Patched version:** 3.11.0

It is recommended to upgrade to version 3.11.0 or later and to avoid opening untrusted model files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9906
- https://github.com/keras-team/keras/pull/21429
- https://github.com/keras-team/keras/commit/713172ab56b864e59e2aa79b1a51b0e728bba858
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.11.0
- https://github.com/pypa/advisory-database/tree/main/vulns/keras/PYSEC-2025-76.yaml
- https://osv.dev/vulnerability/CVE-2025-9906
