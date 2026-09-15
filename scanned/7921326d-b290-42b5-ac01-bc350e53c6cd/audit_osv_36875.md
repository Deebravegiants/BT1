# [C] KTransformers Unsafe Deserialization RCE via balance_serve

## Summary
Severity: Critical
Advisory: CVE-2026-26210
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-26210
Type: osv

## Details
KTransformers through 0.5.3 contains an unsafe deserialization vulnerability in the balance_serve backend mode where the scheduler RPC server binds a ZMQ ROUTER socket to all interfaces with no authentication and deserializes incoming messages using pickle.loads() without validation. Attackers can send a crafted pickle payload to the exposed ZMQ socket to execute arbitrary code on the server with the privileges of the ktransformers process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26210
- https://www.vulncheck.com/advisories/ktransformers-unsafe-deserialization-rce-via-balance-serve
- https://github.com/kvcache-ai/ktransformers/pull/1944
- https://github.com/kvcache-ai/ktransformers
- https://chocapikk.com/posts/2026/ktransformers-pickle-rce/
