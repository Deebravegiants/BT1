# [H] Arbitrary File Write in mudler/LocalAI

## Summary
Severity: High
Advisory: CVE-2024-6868
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-6868
Type: osv

## Details
mudler/LocalAI version 2.17.1 allows for arbitrary file write due to improper handling of automatic archive extraction. When model configurations specify additional files as archives (e.g., .tar), these archives are automatically extracted after downloading. This behavior can be exploited to perform a 'tarslip' attack, allowing files to be written to arbitrary locations on the server, bypassing checks that normally restrict files to the models directory. This vulnerability can lead to remote code execution (RCE) by overwriting backend assets used by the server.

## References
- https://huntr.com/bounties/752d2376-2d9a-4e17-b462-3c267f9dd229
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6868.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6868
- https://github.com/mudler/localai/commit/a181dd0ebc5d3092fc50f61674d552604fe8ef9c
