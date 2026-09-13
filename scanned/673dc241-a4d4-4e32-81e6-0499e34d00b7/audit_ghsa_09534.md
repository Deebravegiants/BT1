# [H] Eclipse BaSyx Java Server SDK vulnerable to Server-Side Request Forgery

## Summary
Severity: High
Advisory: GHSA-gx3v-wxfj-8h24
CVE: CVE-2026-7412
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-gx3v-wxfj-8h24
Type: github-advisory

## Affected
- Maven: `org.eclipse.basyx:basyx.sdk` — affected >=0 <2.0.0-milestone-10

## Details
In Eclipse BaSyx Java Server SDK versions prior to 2.0.0-milestone-10, the Operation Delegation feature fails to validate the destination URI of delegated requests. An unauthenticated remote attacker can exploit this design flaw to force the BaSyx server to execute blind HTTP POST requests to arbitrary internal or external targets. This allows an attacker to bypass network segmentation and pivot into isolated internal IT/OT infrastructure or target Cloud Metadata services (IMDS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7412
- https://github.com/eclipse-basyx/basyx-java-sdk
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/103
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/423
