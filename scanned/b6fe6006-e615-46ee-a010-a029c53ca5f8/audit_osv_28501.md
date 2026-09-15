# [H] CVE-2024-33782

## Summary
Severity: High
Advisory: CVE-2024-33782
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2024-33782
Type: osv

## Details
MP-SPDZ v0.3.8 was discovered to contain a stack overflow via the function OTExtensionWithMatrix::extend in /OT/OTExtensionWithMatrix.cpp. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted message.

## References
- https://github.com/FudanMPL/Vulnerabilities-in-MPC-Framework/tree/main/MP-SPDZ/stack-buffer-overflow-OTExtensionWithMatrix
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33782.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33782
