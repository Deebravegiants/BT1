# [H] libcupsfilters's cfGetPrinterAttributes5 does not validate IPP attributes returned from an IPP server

## Summary
Severity: High
Advisory: CVE-2024-47076
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-47076
Type: osv

## Details
CUPS is a standards-based, open-source printing system, and `libcupsfilters` contains the code of the filters of the former `cups-filters` package as library functions to be used for the data format conversion tasks needed in Printer Applications. The `cfGetPrinterAttributes5` function in `libcupsfilters` does not sanitize IPP attributes returned from an IPP server. When these IPP attributes are used, for instance, to generate a PPD file, this can lead to attacker controlled data to be provided to the rest of the CUPS system.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00048.html
- https://www.cups.org
- https://www.evilsocket.net/2024/09/26/Attacking-UNIX-systems-via-CUPS-Part-I
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47076.json
- https://github.com/OpenPrinting/cups-browsed/security/advisories/GHSA-rj88-6mr5-rcw8
- https://github.com/OpenPrinting/cups-filters/security/advisories/GHSA-p9rh-jxmq-gq47
- https://github.com/OpenPrinting/libcupsfilters/security/advisories/GHSA-w63j-6g73-wmg5
- https://github.com/OpenPrinting/libppd/security/advisories/GHSA-7xfx-47qg-grp6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47076
- https://security.netapp.com/advisory/ntap-20241011-0001/
- https://github.com/OpenPrinting/libcupsfilters/commit/95576ec3d20c109332d14672a807353cdc551018
