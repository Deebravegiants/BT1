# [C] Feast < 0.63.0 Unauthenticated RCE via ApplyFeatureView gRPC Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-56121
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56121
Type: osv

## Details
Feast before 0.63.0 contains an unsafe deserialization vulnerability that allows unauthenticated or unauthorized attackers to achieve remote code execution by sending a crafted gRPC request to the registry server. The user_defined_function.body field of an OnDemandFeatureView spec is decoded from base64 and passed to dill.loads() before any authorization check is performed, enabling attackers to embed a malicious serialized Python object with an arbitrary __reduce__ method to execute OS commands as the feast service account.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-56121.json
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/security/cve/CVE-2026-56121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56121.json
- https://github.com/feast-dev/feast/releases/tag/v0.63.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-56121
- https://www.vulncheck.com/advisories/feast-unauthenticated-rce-via-applyfeatureview-grpc-deserialization
- https://bugzilla.redhat.com/show_bug.cgi?id=2492229
- https://github.com/feast-dev/feast/commit/835cda8e2c1359f1f496ad72701dbd6a73bdb25a
- https://github.com/feast-dev/feast
- https://huntr.com/bounties/d64b8111-180b-46ba-afa3-c877fda2ede6
