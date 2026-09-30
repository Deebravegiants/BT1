# [C] CVE-2022-30547

## Summary
Severity: Critical
Advisory: CVE-2022-30547
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-30547
Type: osv

## Details
A directory traversal vulnerability exists in the unzipDirectory functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. A specially-crafted HTTP request can lead to arbitrary command execution. An attacker can send an HTTP request to trigger this vulnerability.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1547
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30547.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30547
