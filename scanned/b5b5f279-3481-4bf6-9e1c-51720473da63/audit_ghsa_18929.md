# [M] Peppol-py is vulnerable to XXE attacks due to Saxon configuration

## Summary
Severity: Medium
Advisory: GHSA-24hm-wm2h-h8w7
CVE: CVE-2025-66371
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-28
Source: https://github.com/advisories/GHSA-24hm-wm2h-h8w7
Type: github-advisory

## Affected
- PyPI: `peppol_py` — affected >=0 <1.1.1

## Details
Peppol-py before 1.1.1 allows XXE attacks because of the Saxon configuration. When validating XML-based invoices, the XML parser could read files from the filesystem and expose their content to a remote host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66371
- https://github.com/iterasdev/peppol-py/pull/16
- https://github.com/iterasdev/peppol-py/commit/349a4bff8adb6205ea411bac8d7a06da0477abd7
- https://github.com/iterasdev/peppol-py
- https://github.com/iterasdev/peppol-py/releases/tag/1.1.1
- https://invoice.secvuln.info
