# [C] pyodide sandbox option is insecure

## Summary
Severity: Critical
Advisory: CVE-2026-24002
Aliases: GHSA-7xvx-8pf2-pv5g
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24002
Type: osv

## Details
Grist is spreadsheet software using Python as its formula language. Grist offers several methods for running those formulas in a sandbox, for cases where the user may be working with untrusted spreadsheets. One such method runs them in pyodide, but pyodide on node does not have a useful sandbox barrier. If a user of Grist sets `GRIST_SANDBOX_FLAVOR` to `pyodide` and opens a malicious document, that document could run arbitrary processes on the server hosting Grist. The problem has been addressed in Grist version 1.7.9 and up, by running pyodide under deno. As a workaround, a user can use the gvisor-based sandbox by setting  `GRIST_SANDBOX_FLAVOR` to `gvisor`.

## References
- https://support.getgrist.com/self-managed/#how-do-i-sandbox-documents
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24002.json
- https://github.com/gristlabs/grist-core/security/advisories/GHSA-7xvx-8pf2-pv5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-24002
