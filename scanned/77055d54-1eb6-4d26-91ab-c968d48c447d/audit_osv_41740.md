# [C] ktransformers Unauthenticated Pickle Deserialization RCE via ZMQ

## Summary
Severity: Critical
Advisory: CVE-2026-63767
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63767
Type: osv

## Details
ktransformers through 0.6.3, fixed in commit def0f93, contains an unauthenticated pickle deserialization vulnerability that allows remote attackers to execute arbitrary commands by sending crafted pickle payloads to the SchedulerServer ZMQ ROUTER socket bound to all interfaces. Attackers can exploit malicious __reduce__ methods embedded in crafted pickle payloads to execute arbitrary shell commands as the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63767.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63767
- https://www.vulncheck.com/advisories/ktransformers-unauthenticated-pickle-deserialization-rce-via-zmq
- https://github.com/kvcache-ai/ktransformers/issues/2087
- https://github.com/kvcache-ai/ktransformers/commit/def0f9313d6e063b5c5ccdfa1f6707f7a40dfdca
- https://github.com/kvcache-ai/ktransformers/pull/2091
- https://github.com/kvcache-ai/ktransformers
