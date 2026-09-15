# [C] vLLM Vulnerable to Remote Code Execution via Mooncake Integration

## Summary
Severity: Critical
Advisory: GHSA-hj4w-hm2g-p6w5
CVE: CVE-2025-32444
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-hj4w-hm2g-p6w5
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.6.5 <0.8.5

## Details
## Impacted Deployments

**Note that vLLM instances that do NOT make use of the mooncake integration are NOT vulnerable.**

## Description

vLLM integration with mooncake is vaulnerable to remote code execution due to using `pickle` based serialization over unsecured ZeroMQ sockets. The vulnerable sockets were set to listen on all network interfaces, increasing the likelihood that an attacker is able to reach the vulnerable ZeroMQ sockets to carry out an attack.


This is a similar to [GHSA - x3m8 - f7g5 - qhm7](https://github.com/vllm-project/vllm/security/advisories/GHSA-x3m8-f7g5-qhm7), the problem is in

https://github.com/vllm-project/vllm/blob/32b14baf8a1f7195ca09484de3008063569b43c5/vllm/distributed/kv_transfer/kv_pipe/mooncake_pipe.py#L179

Here [recv_pyobj()](https://github.com/zeromq/pyzmq/blob/453f00c5645a3bea40d79f53aa8c47d85038dc2d/zmq/sugar/socket.py#L961) Contains implicit `pickle.loads()`, which leads to potential RCE.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-hj4w-hm2g-p6w5
- https://github.com/vllm-project/vllm/security/advisories/GHSA-x3m8-f7g5-qhm7
- https://nvd.nist.gov/vuln/detail/CVE-2025-32444
- https://github.com/vllm-project/vllm/commit/a5450f11c95847cf51a17207af9a3ca5ab569b2c
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2025-42.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/32b14baf8a1f7195ca09484de3008063569b43c5/vllm/distributed/kv_transfer/kv_pipe/mooncake_pipe.py#L179
