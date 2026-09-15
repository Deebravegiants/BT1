# [M] BIT-tomcat-2020-13943

## Summary
Severity: Medium
Advisory: BIT-tomcat-2020-13943
Aliases: CVE-2020-13943, GHSA-f268-65qc-98vg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2020-13943
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=9.0.0 <9.0.38

## Details
If an HTTP/2 client connecting to Apache Tomcat 9.0.0 through 9.0.37 or 8.5.0 to 8.5.57 exceeded the agreed maximum number of concurrent streams for a connection (in violation of the HTTP/2 protocol), it was possible that a subsequent request made on that connection could contain HTTP headers - including HTTP/2 pseudo headers - from a previous request rather than the intended headers. This could lead to users seeing responses for unexpected resources.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00021.html
- https://lists.apache.org/thread.html/r4a390027eb27e4550142fac6c8317cc684b157ae314d31514747f307%40%3Cannounce.tomcat.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/10/msg00019.html
- https://security.netapp.com/advisory/ntap-20201016-0007/
- https://www.debian.org/security/2021/dsa-4835
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-13943
