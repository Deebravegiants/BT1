# [C] OpenMed vulnerable to remote code injection through privacy-filter model loading path

## Summary
Severity: Critical
Advisory: GHSA-m3v4-v5gx-7wf5
CVE: CVE-2026-47117
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-02
Source: https://github.com/advisories/GHSA-m3v4-v5gx-7wf5
Type: github-advisory

## Affected
- PyPI: `openmed` — affected >=0 <1.5.2

## Details
OpenMed before 1.5.2 contains a remote code execution vulnerability in the PII privacy-filter model loading path. The privacy-filter dispatcher used broad substring matching on the user-supplied `model_name` parameter, allowing a value such as `attacker/foo-privacy-filter-bar` to route through a path that loads Hugging Face models with `trust_remote_code=True`. An unauthenticated attacker can supply a malicious model repository containing custom Transformers code via auto_map in `config.json` or `tokenizer_config.json`, which is imported and executed with the privileges of the OpenMed service process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47117
- https://github.com/maziyarpanahi/openmed/pull/59
- https://github.com/maziyarpanahi/openmed/commit/98724f65df98d7518b9006e6356740aa36c2f224
- https://github.com/maziyarpanahi/openmed/releases/tag/v1.5.2
- https://www.vulncheck.com/advisories/openmed-remote-code-execution-via-pii-model-loading
- github.com/maziyarpanahi/openmed
