# [C] Horovod Vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-mrhh-3ggq-23p2
CVE: CVE-2024-10190
CWE: CWE-502, CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-mrhh-3ggq-23p2
Type: github-advisory

## Affected
- PyPI: `horovod` — affected >=0

## Details
Horovod versions up to and including v0.28.1 are vulnerable to unauthenticated remote code execution. The vulnerability is due to improper handling of base64-encoded data in the `ElasticRendezvousHandler`, a subclass of `KVStoreHandler`. Specifically, the `_put_value` method in `ElasticRendezvousHandler` calls `codec.loads_base64(value)`, which eventually invokes `cloudpickle.loads(decoded)`. This allows an attacker to send a malicious pickle object via a PUT request, leading to arbitrary code execution on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10190
- https://github.com/horovod/horovod
- https://huntr.com/bounties/3e398d1f-70c2-4e05-ae22-f5d66b19a754
