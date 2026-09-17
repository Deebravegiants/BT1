# [H] CVE-2025-11002

## Summary
Severity: High
Advisory: CVE-2025-11002
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-11002
Type: osv

## Details
7-Zip ZIP File Parsing Directory Traversal Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of 7-Zip. Interaction with this product is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the handling of symbolic links in ZIP files. Crafted data in a ZIP file can cause the process to traverse to unintended directories. An attacker can leverage this vulnerability to execute code in the context of a service account. Was ZDI-CAN-26743.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-25-950/
