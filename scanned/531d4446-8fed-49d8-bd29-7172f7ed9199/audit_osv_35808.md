# [C] CVE-2026-14890

## Summary
Severity: Critical
Advisory: CVE-2026-14890
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-14890
Type: osv

## Details
SGLang uses an expert-parallel backup subsystem that exposes a ZeroMQ PULL socket on a routable network interface that does not contain authentication or deserialization safeguards, allowing an attacker to provide a malicious pickle file that results in unauthenticated remote code execution when the feature is enabled and the service is reachable over the network.

## References
- http://vince.cert.org/vuls/id/326070
- https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/elastic_ep/expert_backup_manager.py
- https://www.kb.cert.org/vuls/id/326070
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14890.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14890
