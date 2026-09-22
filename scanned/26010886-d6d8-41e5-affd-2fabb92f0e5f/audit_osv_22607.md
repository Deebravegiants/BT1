# [H] CVE-2022-33148

## Summary
Severity: High
Advisory: CVE-2022-33148
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-33148
Type: osv

## Details
A sql injection vulnerability exists in the ObjectYPT functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. A specially-crafted HTTP request can lead to a SQL injection. An attacker can send an HTTP request to trigger this vulnerability.This vulnerability exists in the Live Schedules plugin, allowing an attacker to inject SQL by manipulating the title parameter.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1551
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/33xxx/CVE-2022-33148.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-33148
