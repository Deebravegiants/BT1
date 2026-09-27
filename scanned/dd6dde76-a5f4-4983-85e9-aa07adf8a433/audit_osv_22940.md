# [H] Exposed Dangerous Method or Function in qmpaas/leadshop

## Summary
Severity: High
Advisory: CVE-2022-4136
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2022-11-24
Source: https://osv.dev/vulnerability/CVE-2022-4136
Type: osv

## Details
Dangerous method exposed which can lead to RCE in qmpass/leadshop v1.4.15 allows an attacker to control the target host by calling any function in leadshop.php via the GET method.

## References
- https://huntr.dev/bounties/fe418ae1-7c80-4d91-8a5a-923d60ba78c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4136.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4136
- https://github.com/qmpaas/leadshop/commit/f27e9ca5c93eaadda1097396b65c234b16186d67
