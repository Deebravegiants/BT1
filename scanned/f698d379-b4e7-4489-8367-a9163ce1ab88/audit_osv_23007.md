# [H] CVE-2022-41981

## Summary
Severity: High
Advisory: CVE-2022-41981
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41981
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the TGA file format parser of OpenImageIO v2.3.19.0. A specially-crafted targa file can lead to out of bounds read and write on the process stack, which can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1628
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41981.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41981
