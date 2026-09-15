# [C] AI Tensor Engine for ROCm (AITER) 0.1.14 Unauthenticated RCE via MessageQueue.recv() Pickle Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-49121
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-49121
Type: osv

## Details
AI Tensor Engine for ROCm (AITER) through 0.1.14 contains an unauthenticated remote code execution vulnerability in the MessageQueue.recv() function within shm_broadcast.py that allows unauthenticated remote attackers to execute arbitrary code by sending a malicious pickle payload to a ZMQ SUB socket with no authentication, HMAC, or format validation. Attackers who can reach the writer XPUB endpoint on the cluster network or supply a forged Handle with an attacker-controlled remote_subscribe_addr can deliver a crafted pickle payload that executes arbitrary code simultaneously as the inference worker process on every remote reader worker.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-49121.json
- https://access.redhat.com/security/cve/CVE-2026-49121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49121.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49121
- https://www.vulncheck.com/advisories/ai-tensor-engine-for-rocm-aiter-unauthenticated-rce-via-messagequeue-recv-pickle-deserialization
- https://bugzilla.redhat.com/show_bug.cgi?id=2483882
- https://github.com/ROCm/aiter/issues/3076
- https://github.com/ROCm/aiter/pull/3170
- https://github.com/ROCm/aiter
