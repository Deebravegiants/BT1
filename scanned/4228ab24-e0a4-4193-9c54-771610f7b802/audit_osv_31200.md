# [H] Undertow: response write hangs in case of java 17 tlsv1.3 newsessionticket

## Summary
Severity: High
Advisory: CVE-2024-5971
Aliases: GHSA-xpp6-8r3j-ww43
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-5971
Type: osv

## Details
A vulnerability was found in Undertow, where the chunked response hangs after the body was flushed. The response headers and body were sent but the client would continue waiting as Undertow does not send the expected 0\r\n termination of the chunked response. This results in uncontrolled resource consumption, leaving the server side to a denial of service attack. This happens only with Java 17 TLSv1.3 scenarios.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://access.redhat.com/errata/RHSA-2024:4392
- https://access.redhat.com/errata/RHSA-2024:4884
- https://access.redhat.com/errata/RHSA-2024:5143
- https://access.redhat.com/errata/RHSA-2024:5144
- https://access.redhat.com/errata/RHSA-2024:5145
- https://access.redhat.com/errata/RHSA-2024:5147
- https://access.redhat.com/errata/RHSA-2024:6508
- https://access.redhat.com/errata/RHSA-2024:6883
- https://access.redhat.com/security/cve/CVE-2024-5971
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5971
- https://security.netapp.com/advisory/ntap-20240828-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2292211
- https://github.com/undertow-io/undertow
