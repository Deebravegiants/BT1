# [H] CVE-2023-5379

## Summary
Severity: High
Advisory: CVE-2023-5379
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-5379
Type: osv

## Details
A flaw was found in Undertow. When an AJP request is sent that exceeds the max-header-size attribute in ajp-listener, JBoss EAP is marked in an error state by mod_cluster in httpd, causing JBoss EAP to close the TCP connection without returning an AJP response. This happens because mod_proxy_cluster marks the JBoss EAP instance as an error worker when the TCP connection is closed from the backend after sending the AJP request without receiving an AJP response, and stops forwarding. This issue could allow a malicious user could to repeatedly send requests that exceed the max-header-size, causing a Denial of Service (DoS).

## References
- https://access.redhat.com/errata/RHSA-2023:4509
- https://access.redhat.com/errata/RHSA-2025:9582
- https://access.redhat.com/errata/RHSA-2025:9583
- https://access.redhat.com/security/cve/CVE-2023-5379
- https://bugzilla.redhat.com/show_bug.cgi?id=2242099
