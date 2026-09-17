# [H] AutoGPT Platform: Remote Code Execution via Unsafe Pickle Deserialization of Redis Cache Entries

## Summary
Severity: High
Advisory: CVE-2026-33233
Aliases: GHSA-rfg2-37xq-w4m9
CVSS: 7.6 (CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-33233
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. In versions 0.6.34 through 0.6.51, the backend deserializes Redis cache bytes using pickle.loads without integrity/authenticity checks. The write path serializes values with pickle.dumps(...) into Redis and the read path blindly invokes pickle.loads(...) on bytes with no HMAC/signature or strict schema validation gating deserialization. If an attacker can poison a shared-cache key in Redis, arbitrary command execution is possible in the backend container context, affecting confidentiality, integrity, and availability. This issue has been fixed in version 0.6.52.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33233.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-rfg2-37xq-w4m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33233
