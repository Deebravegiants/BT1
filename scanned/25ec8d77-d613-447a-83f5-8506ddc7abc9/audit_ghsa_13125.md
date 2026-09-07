# [H] Undertow vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-65h2-wf7m-q2v8
CVE: CVE-2023-3223
CWE: CWE-400, CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-65h2-wf7m-q2v8
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-parent` — affected >=0 <2.2.24.Final

## Details
A flaw was found in undertow. Servlets annotated with @MultipartConfig may cause an OutOfMemoryError due to large multipart content. This may allow unauthorized users to cause remote Denial of Service (DoS) attack. If the server uses fileSizeThreshold to limit the file size, it's possible to bypass the limit by setting the file name in the request to null.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3223
- https://access.redhat.com/errata/RHSA-2023:4505
- https://access.redhat.com/errata/RHSA-2023:4506
- https://access.redhat.com/errata/RHSA-2023:4507
- https://access.redhat.com/errata/RHSA-2023:4509
- https://access.redhat.com/errata/RHSA-2023:4918
- https://access.redhat.com/errata/RHSA-2023:4919
- https://access.redhat.com/errata/RHSA-2023:4920
- https://access.redhat.com/errata/RHSA-2023:4921
- https://access.redhat.com/errata/RHSA-2023:4924
- https://access.redhat.com/errata/RHSA-2023:7247
- https://access.redhat.com/security/cve/CVE-2023-3223
- https://bugzilla.redhat.com/show_bug.cgi?id=2209689
- https://github.com/undertow-io/undertow
- https://security.netapp.com/advisory/ntap-20231027-0004
