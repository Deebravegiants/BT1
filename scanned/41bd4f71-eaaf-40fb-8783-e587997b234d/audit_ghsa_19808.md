# [C] vLLM deserialization vulnerability in vllm.distributed.GroupCoordinator.recv_object

## Summary
Severity: Critical
Advisory: GHSA-pgr7-mhp5-fgjp
CVE: CVE-2024-9052
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-pgr7-mhp5-fgjp
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0

## Details
vllm-project vllm version 0.6.0 contains a vulnerability in the distributed training API. The function vllm.distributed.GroupCoordinator.recv_object() deserializes received object bytes using pickle.loads() without sanitization, leading to a remote code execution vulnerability.

### Maintainer perspective
Note that vLLM does NOT use the code as described in the report on huntr. The problem only exists if you use these internal APIs in a way that exposes them to a network as described. The vllm team was not involved in the analysis of this report and the decision to assign it a CVE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9052
- https://github.com/github/advisory-database/pull/5444
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/32e7db25365415841ebc7c4215851743fbb1bad1/vllm/distributed/parallel_state.py#L480
- https://github.com/vllm-project/vllm/blob/v0.8.1/vllm/distributed/parallel_state.py#L457
- https://huntr.com/bounties/ea75728f-4efe-4a3d-9f53-33f2c908e9f8
