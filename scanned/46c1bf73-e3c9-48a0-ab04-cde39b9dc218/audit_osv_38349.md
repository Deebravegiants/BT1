# [M] CUPS has a use-after-free in `cupsdDeleteTemporaryPrinters` via dangling subscription pointer

## Summary
Severity: Medium
Advisory: CVE-2026-39316
Aliases: GHSA-pjv5-prqp-46rg
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39316
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, a use-after-free vulnerability exists in the CUPS scheduler (cupsd) when temporary printers are automatically deleted. cupsdDeleteTemporaryPrinters() in scheduler/printers.c calls cupsdDeletePrinter() without first expiring subscriptions that reference the printer, leaving cupsd_subscription_t.dest as a dangling pointer to freed heap memory. The dangling pointer is subsequently dereferenced at multiple code sites, causing a crash (denial of service) of the cupsd daemon. With heap grooming, this can be leveraged for code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39316.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-pjv5-prqp-46rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-39316
