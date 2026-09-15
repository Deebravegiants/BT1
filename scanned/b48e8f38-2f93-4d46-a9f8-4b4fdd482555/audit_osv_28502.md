# [M] CVE-2024-33783

## Summary
Severity: Medium
Advisory: CVE-2024-33783
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2024-33783
Type: osv

## Details
MP-SPDZ v0.3.8 was discovered to contain a segmentation violation via the function osuCrypto::SilentMultiPprfReceiver::expand in /Tools/SilentPprf.cpp. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted message.

## References
- https://github.com/FudanMPL/Vulnerabilities-in-MPC-Framework/tree/main/MP-SPDZ/SEGV-SlientPprf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33783.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33783
