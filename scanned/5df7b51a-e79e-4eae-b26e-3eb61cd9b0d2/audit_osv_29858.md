# [H] libppd's ppdCreatePPDFromIPP2 function does not sanitize IPP attributes when creating the PPD buffer

## Summary
Severity: High
Advisory: CVE-2024-47175
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-47175
Type: osv

## Details
CUPS is a standards-based, open-source printing system, and `libppd` can be used for legacy PPD file support. The `libppd` function `ppdCreatePPDFromIPP2` does not sanitize IPP attributes when creating the PPD buffer. When used in combination with other functions such as `cfGetPrinterAttributes5`, can result in user controlled input and ultimately code execution via Foomatic. This vulnerability can be part of an exploit chain leading to remote code execution (RCE), as described in CVE-2024-47176.

## References
- http://www.openwall.com/lists/oss-security/2024/09/27/3
- https://lists.debian.org/debian-lts-announce/2024/09/msg00047.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2024-0016
- https://www.cups.org
- https://www.evilsocket.net/2024/09/26/Attacking-UNIX-systems-via-CUPS-Part-I
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47175.json
- https://github.com/OpenPrinting/cups-browsed/security/advisories/GHSA-rj88-6mr5-rcw8
- https://github.com/OpenPrinting/cups-filters/security/advisories/GHSA-p9rh-jxmq-gq47
- https://github.com/OpenPrinting/libcupsfilters/security/advisories/GHSA-w63j-6g73-wmg5
- https://github.com/OpenPrinting/libppd/security/advisories/GHSA-7xfx-47qg-grp6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47175
- https://security.netapp.com/advisory/ntap-20241011-0001/
- https://github.com/OpenPrinting/libppd/commit/d681747ebf12602cb426725eb8ce2753211e2477
