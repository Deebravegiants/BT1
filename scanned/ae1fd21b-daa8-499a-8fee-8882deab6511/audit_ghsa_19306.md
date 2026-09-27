# [H] Remote Code Execution Vulnerability in vLLM Multi-Node Cluster Configuration

## Summary
Severity: High
Advisory: GHSA-9pcc-gvx5-r5wm
CVE: CVE-2025-30165
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-9pcc-gvx5-r5wm
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.2 <0.10.0

## Details
### Affected Environments

Note that this issue only affects the V0 engine, which has been off by default since v0.8.0. Further, the issue only applies to a deployment using tensor parallelism across multiple hosts, which we do not expect to be a common deployment pattern.

Since V0 is has been off by default since v0.8.0 and the fix is fairly invasive, we have decided not to fix this issue. Instead we recommend that users ensure their environment is on a secure network in case this pattern is in use.

The V1 engine is not affected by this issue.

### Impact

In a multi-node vLLM deployment using the V0 engine, vLLM uses ZeroMQ for some multi-node communication purposes. The secondary vLLM hosts open a `SUB` ZeroMQ socket and connect to an `XPUB` socket on the primary vLLM host.

https://github.com/vllm-project/vllm/blob/c21b99b91241409c2fdf9f3f8c542e8748b317be/vllm/distributed/device_communicators/shm_broadcast.py#L295-L301

When data is received on this `SUB` socket, it is deserialized with `pickle`. This is unsafe, as it can be abused to execute code on a remote machine.

https://github.com/vllm-project/vllm/blob/c21b99b91241409c2fdf9f3f8c542e8748b317be/vllm/distributed/device_communicators/shm_broadcast.py#L468-L470

Since the vulnerability exists in a client that connects to the primary vLLM host, this vulnerability serves as an escalation point. If the primary vLLM host is compromised, this vulnerability could be used to compromise the rest of the hosts in the vLLM deployment.

Attackers could also use other means to exploit the vulnerability without requiring access to the primary vLLM host. One example would be the use of ARP cache poisoning to redirect traffic to a malicious endpoint used to deliver a payload with arbitrary code to execute on the target machine.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-9pcc-gvx5-r5wm
- https://nvd.nist.gov/vuln/detail/CVE-2025-30165
- https://github.com/advisories/GHSA-9pcc-gvx5-r5wm
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2017.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/c21b99b91241409c2fdf9f3f8c542e8748b317be/vllm/distributed/device_communicators/shm_broadcast.py#L295-L301
- https://github.com/vllm-project/vllm/blob/c21b99b91241409c2fdf9f3f8c542e8748b317be/vllm/distributed/device_communicators/shm_broadcast.py#L468-L470
- https://pypi.org/project/vllm
