# [M] CVE-2022-28710

## Summary
Severity: Medium
Advisory: CVE-2022-28710
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-28710
Type: osv

## Details
An information disclosure vulnerability exists in the chunkFile functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. A specially-crafted HTTP request can lead to arbitrary file read. An attacker can send an HTTP request to trigger this vulnerability.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1550
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28710.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28710
