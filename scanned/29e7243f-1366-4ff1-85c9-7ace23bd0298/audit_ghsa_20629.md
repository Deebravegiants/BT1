# [M] HTML Injection in ActiveMQ Artemis Web Console

## Summary
Severity: Medium
Advisory: GHSA-cv6r-h2fm-pvrp
CVE: CVE-2022-35278
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-cv6r-h2fm-pvrp
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-server` — affected >=0 <2.24.0

## Details
In Apache ActiveMQ Artemis prior to 2.24.0, an attacker could show malicious content and/or redirect users to a malicious URL in the web console by using HTML in the name of an address or queue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35278
- https://lists.apache.org/thread/bh6y81wtotg75337bpvxcjy436zfgf3n
- https://security.netapp.com/advisory/ntap-20221209-0005
