# [H] CVE-2022-32282

## Summary
Severity: High
Advisory: CVE-2022-32282
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-32282
Type: osv

## Details
An improper password check exists in the login functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. An attacker that owns a users' password hash will be able to use it to directly login into the account, leading to increased privileges.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1545
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32282.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32282
