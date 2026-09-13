# [C] vLLM Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5vqr-wprc-cpp7
CVE: CVE-2024-11041
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5vqr-wprc-cpp7
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0

## Details
vllm-project vllm version v0.6.2 contains a vulnerability in the MessageQueue.dequeue() API function. The function uses pickle.loads to parse received sockets directly, leading to a remote code execution vulnerability. An attacker can exploit this by sending a malicious payload to the MessageQueue, causing the victim's machine to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11041
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/7193774b1ff8603ad5bf4598e5efba0d9a39b436/vllm/distributed/device_communicators/shm_broadcast.py#L441-L443
- https://huntr.com/bounties/00136195-11e0-4ad0-98d5-72db066e867f
