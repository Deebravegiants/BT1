# [C] LeRobot Unsafe Deserialization Remote Code Execution via gRPC

## Summary
Severity: Critical
Advisory: CVE-2026-25874
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-25874
Type: osv

## Details
LeRobot through 0.5.1 contains an unsafe deserialization vulnerability in the async inference pipeline where pickle.loads() is used to deserialize data received over unauthenticated gRPC channels without TLS in the policy server and robot client components. An unauthenticated network-reachable attacker can achieve arbitrary code execution on the server or client by sending a crafted pickle payload through the SendPolicyInstructions, SendObservations, or GetActions gRPC calls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25874.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25874
- https://www.vulncheck.com/advisories/lerobot-unsafe-deserialization-remote-code-execution-via-grpc
- https://github.com/huggingface/lerobot/issues/3047
- https://github.com/huggingface/lerobot/issues/3134
- https://github.com/huggingface/lerobot/pull/3048
- https://github.com/huggingface/lerobot
- https://chocapikk.com/posts/2026/lerobot-pickle-rce/
