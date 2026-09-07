# [H] Feast vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-34wm-4hw7-qfjv
CVE: CVE-2025-11157
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-01
Source: https://github.com/advisories/GHSA-34wm-4hw7-qfjv
Type: github-advisory

## Affected
- PyPI: `feast` — affected >=0 <0.54.0

## Details
A high-severity remote code execution vulnerability exists in feast-dev/feast version 0.53.0, specifically in the Kubernetes materializer job located at `feast/sdk/python/feast/infra/compute_engines/kubernetes/main.py`. The vulnerability arises from the use of `yaml.load(..., Loader=yaml.Loader)` to deserialize `/var/feast/feature_store.yaml` and `/var/feast/materialization_config.yaml`. This method allows for the instantiation of arbitrary Python objects, enabling an attacker with the ability to modify these YAML files to execute OS commands on the worker pod. This vulnerability can be exploited before the configuration is validated, potentially leading to cluster takeover, data poisoning, and supply-chain sabotage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11157
- https://github.com/feast-dev/feast/pull/5643
- https://github.com/feast-dev/feast/commit/b2e37ff37953b68ae833f6874ab5bc510a4ca5fb
- https://github.com/feast-dev/feast
- https://huntr.com/bounties/46d4d585-b968-4a76-80ce-872bc5525564
