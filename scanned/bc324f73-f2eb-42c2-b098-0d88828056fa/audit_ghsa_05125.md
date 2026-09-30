# [H] huggingface/transformers: Arbitrary Code Execution During Model Initialization in the LightGlue Model Loading Path

## Summary
Severity: High
Advisory: GHSA-fgcw-684q-jj6r
CVE: CVE-2026-5241
CWE: CWE-829
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-fgcw-684q-jj6r
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <5.5.0

## Details
A vulnerability in the LightGlue model loading path of huggingface/transformers version 5.2.0 allows an attacker-controlled model repository to execute arbitrary code during model initialization. The issue arises because the `trust_remote_code` parameter, intended to prevent remote code execution, is overridden by untrusted serialized configuration data in a nested code path. Specifically, when loading a LightGlue model using `AutoModel.from_pretrained()` with `trust_remote_code=False`, the `LightGlueConfig` reads the `trust_remote_code` value from the untrusted `config.json` file and propagates it into nested `AutoConfig.from_pretrained()` calls. This results in the execution of attacker-provided Python modules, even when the victim explicitly disables remote code execution. The vulnerability poses a high risk for environments such as API inference servers, research notebooks, CI/CD pipelines, and model evaluation workers, potentially leading to credential theft, lateral movement, or persistence/backdoor deployment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5241
- https://github.com/huggingface/transformers/commit/676559d5022b74aaa0cee1cee0842b7f27c5320e
- https://access.redhat.com/errata/RHSA-2026:34456
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:42644
- https://access.redhat.com/security/cve/CVE-2026-5241
- https://bugzilla.redhat.com/show_bug.cgi?id=2484384
- https://github.com/huggingface/transformers
- https://github.com/pypa/advisory-database/tree/main/vulns/transformers/PYSEC-2026-2290.yaml
- https://huntr.com/bounties/ceb3ce1a-4c45-497a-b25e-cb9a7685e619
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-5241.json
