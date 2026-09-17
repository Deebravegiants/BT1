# [M] Apache Tomcat: WebSocket DoS with incomplete closing handshake

## Summary
Severity: Medium
Advisory: BIT-tomcat-2024-23672
Aliases: CVE-2024-23672, GHSA-v682-8vv8-vpwr
Ecosystem: Bitnami
Published: 2025-07-17
Source: https://osv.dev/vulnerability/BIT-tomcat-2024-23672
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=10.0.0 <10.1.19

## Details
Denial of Service via incomplete cleanup vulnerability in Apache Tomcat. It was possible for WebSocket clients to keep WebSocket connections open leading to increased resource consumption.This issue affects Apache Tomcat: from 11.0.0 through 11.0.0, from 10.1.0 through 10.1.18, from 9.0.0 through 9.0.85, from 8.5.0 through 8.5.98.

Older, EOL versions may also be affected.


Users are recommended to upgrade to version 11.0.0, 10.1.19, 9.0.86 or 8.5.99 which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/03/13/4
- https://lists.apache.org/thread/cmpswfx6tj4s7x0nxxosvfqs11lvdx2f
- https://lists.debian.org/debian-lts-announce/2024/04/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3UWIS5MMGYDZBLJYT674ZI5AWFHDZ46B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/736G4GPZWS2DSQO5WKXO3G6OMZKFEK55/
- https://nvd.nist.gov/vuln/detail/CVE-2024-23672
- https://security.netapp.com/advisory/ntap-20240402-0002/
