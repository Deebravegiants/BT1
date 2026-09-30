# [H] autogluon.multimodal vulnerable to unsafe YAML deserialization

## Summary
Severity: High
Advisory: GHSA-6h2x-4gjf-jc5w
CWE: CWE-502
Ecosystem: PyPI
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-6h2x-4gjf-jc5w
Type: github-advisory

## Affected
- PyPI: `autogluon.multimodal` — affected >=0.4.0 <0.4.3
- PyPI: `autogluon.multimodal` — affected >=0.5.0 <0.5.2

## Details
### Impact

A potential unsafe deserialization issue exists within the `autogluon.multimodal` module, where YAML files are loaded via `yaml.load()` instead of `yaml.safe_load()`. The deserialization of untrusted data may allow an unprivileged third party to cause remote code execution, denial of service, and impact to both confidentiality and integrity.

Impacted versions: `>=0.4.0;<0.4.3`, `>=0.5.0;<0.5.2`.

### Patches
The patches are included in `autogluon.multimodal==0.4.3`, `autogluon.multimodal==0.5.2` and Deep Learning Containers `0.4.3` and `0.5.2`.

### Workarounds
Do not load data which originated from an untrusted source, or that could have been tampered with. **Only load data you trust.**

### References
* https://cwe.mitre.org/data/definitions/502.html
* https://www.cvedetails.com/cve/CVE-2017-18342/

## References
- https://github.com/awslabs/autogluon/security/advisories/GHSA-6h2x-4gjf-jc5w
- https://github.com/awslabs/autogluon/pull/1987
- https://github.com/awslabs/autogluon/commit/23a37e74e58d03055c84a1b89c5af6c3db296b5e
- https://github.com/awslabs/autogluon
