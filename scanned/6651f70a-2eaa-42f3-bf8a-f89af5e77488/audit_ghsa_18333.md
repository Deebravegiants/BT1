# [M] Kubernetes C# client accepts certificates from any CA without properly verifying the trust chain

## Summary
Severity: Medium
Advisory: GHSA-w7r3-mgwf-4mqq
CVE: CVE-2025-9708
CWE: CWE-295
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-w7r3-mgwf-4mqq
Type: github-advisory

## Affected
- NuGet: `KubernetesClient` — affected >=0 <17.0.14

## Details
A vulnerability exists in the Kubernetes C# client where the certificate validation logic accepts properly constructed certificates from any Certificate Authority (CA) without properly verifying the trust chain. This flaw allows a malicious actor to present a forged certificate and potentially intercept or manipulate communication with the Kubernetes API server, leading to possible man-in-the-middle attacks and API impersonation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9708
- https://github.com/kubernetes/kubernetes/issues/134063
- https://github.com/kubernetes-client/csharp
- https://groups.google.com/g/kubernetes-security-announce/c/rLopt2Msvbw/m/rK6XeNw2CgAJ
- http://www.openwall.com/lists/oss-security/2025/09/16/1
