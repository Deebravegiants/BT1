# [M] kevinsawicki/http-request Missing certificate validation

## Summary
Severity: Medium
Advisory: GHSA-8mx3-gp3p-vgg7
CVE: CVE-2019-1010206
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8mx3-gp3p-vgg7
Type: github-advisory

## Affected
- Maven: `com.github.kevinsawicki:http-request` — affected >=0

## Details
OSS Http Request (kevinsawicki/http-request) is missing SSL/TLS certificate validation. The impact is: certificate spoofing. The component is: use this library when https communication. The attack vector is: certificate spoofing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010206
- https://github.com/kevinsawicki/http-request/blob/master/lib/src/main/java/com/github/kevinsawicki/http/HttpRequest.java
