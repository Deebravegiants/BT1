# [H] Cleartext Transmission of Sensitive Information in Apache MINA

## Summary
Severity: High
Advisory: GHSA-5h29-qq92-wj7f
CVE: CVE-2019-0231
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5h29-qq92-wj7f
Type: github-advisory

## Affected
- Maven: `org.apache.mina:mina-core` — affected >=0 <2.0.21
- Maven: `org.apache.mina:mina-core` — affected >=2.1.0 <2.1.1

## Details
Handling of the close_notify SSL/TLS message does not lead to a connection closure, leading the server to retain the socket opened and to have the client potentially receive clear text messages afterward. Mitigation: 2.0.20 users should migrate to 2.0.21, 2.1.0 users should migrate to 2.1.1. This issue affects: Apache MINA.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0231
- http://mina.apache.org/mina-project/index.html#mina-211-mina-2021-released-posted-on-april-14-2019
