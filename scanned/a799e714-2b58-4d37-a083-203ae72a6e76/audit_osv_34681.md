# [C] CVE-2025-63721

## Summary
Severity: Critical
Advisory: CVE-2025-63721
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-63721
Type: osv

## Details
HummerRisk thru v1.5.0 is using a vulnerable Snakeyaml component, allowing attackers with normal user privileges to hit the /rule/add API and thereby achieve RCE and take over the server.

## References
- https://gist.github.com/k1ng0fic3/e8c8c9353fff8fa95e2c2952587e9266
- https://github.com/k1ng0fic3/secrisk/blob/main/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63721.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63721
