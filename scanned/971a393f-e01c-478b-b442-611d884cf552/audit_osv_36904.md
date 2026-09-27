# [H] CVE-2026-26746

## Summary
Severity: High
Advisory: CVE-2026-26746
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26746
Type: osv

## Details
OpenSourcePOS 3.4.1 contains a Local File Inclusion (LFI) vulnerability in the Sales.php::getInvoice() function. An attacker can read arbitrary files on the web server by manipulating the Invoice Type configuration. This issue can be chained with the file upload functionality to achieve Remote Code Execution (RCE).

## References
- https://github.com/hungnqdz/CVE-2026-26746/blob/main/CVE-2026-26746.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26746.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26746
- https://github.com/opensourcepos/opensourcepos
