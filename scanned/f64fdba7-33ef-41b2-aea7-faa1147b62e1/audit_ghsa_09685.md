# [H] Ray: Remote Code Execution via Parquet Arrow Extension Type Deserialization

## Summary
Severity: High
Advisory: GHSA-mw35-8rx3-xf9r
CVE: CVE-2026-41486
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-mw35-8rx3-xf9r
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=2.49.0 <2.55.0

## Details
Ray Data registers custom Arrow extension types (`ray.data.arrow_tensor`, `ray.data.arrow_tensor_v2`, `ray.data.arrow_variable_shaped_tensor`) globally in PyArrow. When PyArrow reads a Parquet file containing one of these extension types, it calls `__arrow_ext_deserialize__` on the field's metadata bytes. Ray's implementation passes these bytes directly to `cloudpickle.loads()`, achieving arbitrary code execution during schema parsing, before any row data is read.

In May 2024, Ray fixed a related vulnerability in `PyExtensionType`-based extension types ([issue #41314](https://github.com/ray-project/ray/issues/41314), [PR #45084](https://github.com/ray-project/ray/pull/45084)). In July 2025, [PR #54831](https://github.com/ray-project/ray/pull/54831) introduced `cloudpickle.loads()` into the replacement extension types' deserialization path, reintroducing the same class of vulnerability.

## Impact

- **Affected versions**: Ray 2.49.0 through 2.54.0 (latest release as of March 2026). The vulnerable `_deserialize_with_fallback` function with `cloudpickle.loads()` was introduced in commit `f6d21db1a4` ([PR #54831](https://github.com/ray-project/ray/pull/54831), July 2025), first released in Ray 2.49.0.
- **Affected configurations**: Any process that uses Ray Data and reads Parquet files. The extension types are registered globally in PyArrow, so all Parquet reads in the process are affected, including `ray.data.read_parquet()`, `pyarrow.parquet.read_table()`, `pandas.read_parquet()`, etc.
- **Attacker prerequisites**: The attacker must place a crafted Parquet file where a Ray Data pipeline reads it. No authentication or cluster access is required. The Parquet file must contain a column with a `ray.data.arrow_tensor` (or v2, or variable-shaped) extension type name, which makes this a targeted attack against Ray Data users.

## References
- https://github.com/ray-project/ray/security/advisories/GHSA-mw35-8rx3-xf9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41486
- https://github.com/ray-project/ray/pull/54831
- https://github.com/ray-project/ray/pull/62056
- https://github.com/ray-project/ray/commit/c02bd31ae31996805868baa446a131a8d304525f
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.55.0
