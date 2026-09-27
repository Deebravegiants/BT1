# [H] CVE-2018-6336

## Summary
Severity: High
Advisory: CVE-2018-6336
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6336
Type: osv

## Details
An issue was discovered in osquery. A maliciously crafted Universal/fat binary can evade third-party code signing checks. By not completing full inspection of the Universal/fat binary, the user of the third-party tool will believe that the code is signed by Apple, but the malicious unsigned code will execute. This issue affects osquery prior to v3.2.7

## References
- https://www.okta.com/security-blog/2018/06/issues-around-third-party-apple-code-signing-checks/
