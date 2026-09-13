# [M] Denial of service from malicious signature in kyverno

## Summary
Severity: Medium
Advisory: CVE-2023-42816
Aliases: GHSA-4mp4-46gq-hv3r, GO-2023-2338
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:N/A:H)
Published: 2023-11-13
Source: https://osv.dev/vulnerability/CVE-2023-42816
Type: osv

## Details
Kyverno is a policy engine designed for Kubernetes. A security vulnerability was found in Kyverno where an attacker could cause denial of service of Kyverno. The vulnerability was in Kyvernos Notary verifier. An attacker would need control over the registry from which Kyverno would fetch signatures. With such a position, the attacker could return a malicious response to Kyverno, when Kyverno would send a request to the registry. The malicious response would cause denial of service of Kyverno, such that other users' admission requests would be blocked from being processed. This is a vulnerability in a new component released in v1.11.0. The only users affected by this are those that have been building Kyverno from source at the main branch which is not encouraged. Users consuming official Kyverno releases are not affected. There are no known cases of this vulnerability being exploited in the wild.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42816.json
- https://github.com/kyverno/kyverno/security/advisories/GHSA-4mp4-46gq-hv3r
- https://nvd.nist.gov/vuln/detail/CVE-2023-42816
- https://github.com/kyverno/kyverno/commit/80d139bb5d1d9d7e907abe851b97dc73821a5be2
- https://github.com/kyverno/kyverno/commit/fec2992e3f9fcd6b9c62267522c09b182e7df73b
- https://github.com/kyverno/kyverno/pull/8428
