# [C] SSRF - file:// unsanitized access to underlying host files

## Summary
Severity: Critical
Advisory: CVE-2024-0440
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-02-25
Source: https://osv.dev/vulnerability/CVE-2024-0440
Type: osv

## Details
Attacker, with permission to submit a link or submits a link via POST  to be collected that is using the file:// protocol can then introspect host files and other relatively stored files.

## References
- https://huntr.com/bounties/263fd7eb-f9a9-4578-9655-0e28c609272f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0440.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0440
- https://github.com/mintplex-labs/anything-llm/commit/1563a1b20f72846d617a88510970d0426ab880d3
