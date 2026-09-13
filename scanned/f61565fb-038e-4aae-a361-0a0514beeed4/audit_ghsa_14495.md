# [H] Karate has vulnerable dependency on json-smart package (CVE-2023-1370)

## Summary
Severity: High
Advisory: GHSA-5x5q-8cgm-2hjq
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-5x5q-8cgm-2hjq
Type: github-advisory

## Affected
- Maven: `com.intuit.karate:karate-core` — affected >=1.3.1 <1.4.0

## Details
### Summary
The CVE 
![image](https://user-images.githubusercontent.com/2663049/229081854-1155c041-56fa-48ca-a7ff-f2f085b845fd.png)


### How to fix it
Very simple, just upgrade json-path package to 2.8.0 (from 2.7.0) inside karate-core pom.xml ;)

## References
- https://github.com/karatelabs/karate/security/advisories/GHSA-5x5q-8cgm-2hjq
- https://github.com/oswaldobapvicjr/jsonmerge/security/advisories/GHSA-493p-pfq6-5258
- https://nvd.nist.gov/vuln/detail/CVE-2023-1370
- https://github.com/karatelabs/karate
