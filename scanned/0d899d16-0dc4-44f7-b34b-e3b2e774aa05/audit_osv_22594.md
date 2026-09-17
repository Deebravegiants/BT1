# [M] CVE-2022-32769

## Summary
Severity: Medium
Advisory: CVE-2022-32769
CVSS: 4.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-32769
Type: osv

## Details
Multiple authentication bypass vulnerabilities exist in the objects id handling functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. A specially-crafted HTTP request by an authenticated user can lead to unauthorized access and takeover of resources. An attacker can send an HTTP request to trigger this vulnerability.This vulnerability exists in the Playlists plugin, allowing an attacker to bypass authentication by guessing a sequential ID, allowing them to take over the another user's playlists.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1536
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32769.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32769
