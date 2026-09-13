# [C] Remote code execution in Spring Cloud Data Flow

## Summary
Severity: Critical
Advisory: GHSA-p528-3mvf-gr87
CVE: CVE-2024-37084
CWE: CWE-22, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-25
Source: https://github.com/advisories/GHSA-p528-3mvf-gr87
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-skipper` — affected >=0 <2.11.4

## Details
In Spring Cloud Data Flow versions prior to 2.11.4, a malicious user who has access to the Skipper server api can use a crafted upload request to write an arbitrary file to any location on the file system which could lead to compromising the server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37084
- https://github.com/spring-cloud/spring-cloud-dataflow
- https://spring.io/security/cve-2024-37084
