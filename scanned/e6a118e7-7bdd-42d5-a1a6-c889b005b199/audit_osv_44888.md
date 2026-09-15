# [M] Cups: openprinting cups: heap out-of-bounds read in cupsutf32toutf8() via missing source-length bound

## Summary
Severity: Medium
Advisory: CVE-2026-87875
Aliases: GHSA-559w-7676-3xrq
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87875
Type: osv

## Details
The cupsUTF32ToUTF8() function in CUPS's cups/transcode.c lacks a source-length bound and can read past the end of the source buffer, resulting in a heap out-of-bounds read. This is reachable via SNMP supply-description parsing in backend/snmp-supplies.c with attacker-controlled content.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-87875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87875.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-559w-7676-3xrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-87875
- https://bugzilla.redhat.com/show_bug.cgi?id=2530994
- https://github.com/OpenPrinting/cups/commit/0c6842fc615e8afa284136a092da8178abf5f142
- https://github.com/OpenPrinting/cups/commit/2b1dc178a2d2325135b855142e384f4e8c42d8e4
