# [M] Trustyai-explainability: command injection via lmevaljob cr

## Summary
Severity: Medium
Advisory: CVE-2025-6193
CVSS: 5.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L)
Published: 2025-06-20
Source: https://osv.dev/vulnerability/CVE-2025-6193
Type: osv

## Details
A command injection vulnerability was discovered in the TrustyAI Explainability toolkit. Arbitrary commands placed in certain fields of a LMEValJob custom resource (CR) may be executed in the LMEvalJob pod's terminal. This issue can be exploited via a maliciously crafted LMEvalJob by a user with permissions to deploy a CR.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:5807
- https://access.redhat.com/security/cve/CVE-2025-6193
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6193.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6193
- https://bugzilla.redhat.com/show_bug.cgi?id=2374032
- https://github.com/trustyai-explainability/trustyai-service-operator/pull/504
- https://github.com/trustyai-explainability/trustyai-service-operator
