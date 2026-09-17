# [C] LMDeploy Remote Code Execution via Unsafe Pickle Deserialization in the Disaggregated Serving Peer Connector

## Summary
Severity: Critical
Advisory: CVE-2026-76850
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76850
Type: osv

## Details
LMDeploy deserializes disaggregated-serving peer messages with pickle. The handle_zmq_recv coroutine in lmdeploy/pytorch/disagg/conn/engine_conn.py reads peer-to-peer cache-free requests with recv_pyobj(), which deserializes the received bytes with pickle.loads(), and the isinstance check against DistServeCacheFreeRequest runs only after deserialization has already completed. The peer that supplies those bytes is caller-controlled: p2p_connect passes remote_engine_endpoint_info.zmq_address from the request body to connect() on the ZMQ PULL socket, and the POST /distserve/p2p_initialize and /distserve/p2p_connect endpoints in lmdeploy/serve/openai/api_server.py apply no authentication unless the server is started with api_keys, which defaults to None. A remote attacker can direct an engine to pull from a ZMQ endpoint under their control and execute arbitrary code in the engine process. Deployments that do not enable disaggregated serving are not affected, because the receive loop is only started once the migration backend accepts the connection.

## References
- https://pypi.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76850.json
- https://github.com/InternLM/lmdeploy/releases/tag/v0.16.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-76850
- https://www.vulncheck.com/advisories/lmdeploy-remote-code-execution-via-unsafe-pickle-deserialization-in-the-disaggregated-serving-peer-connector
- https://github.com/InternLM/lmdeploy/issues/4804
- https://github.com/InternLM/lmdeploy/commit/f05b4ad8bf2e2d84101a1d63b3c44fadd99223b2
- https://github.com/InternLM/lmdeploy
- https://github.com/InternLM/lmdeploy/blob/v0.15.0/lmdeploy/pytorch/disagg/conn/engine_conn.py#L61
- https://github.com/InternLM/lmdeploy/blob/v0.15.0/lmdeploy/pytorch/disagg/conn/engine_conn.py#L79
