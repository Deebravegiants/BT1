# [M] Apache HTTP Server: mod_proxy prior to 2.4.55 allows a backend to trigger HTTP response splitting

## Summary
Severity: Medium
Advisory: BIT-apache-2022-37436
Aliases: CVE-2022-37436
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2022-37436
Type: osv

## Affected
- Bitnami: `apache` — affected >=0 <2.4.55

## Details
Prior to Apache HTTP Server 2.4.55, a malicious backend can cause the response headers to be truncated early, resulting in some headers being incorporated into the response body. If the later headers have any security purpose, they will not be interpreted by the client.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://security.gentoo.org/glsa/202309-01
- https://nvd.nist.gov/vuln/detail/CVE-2022-37436
