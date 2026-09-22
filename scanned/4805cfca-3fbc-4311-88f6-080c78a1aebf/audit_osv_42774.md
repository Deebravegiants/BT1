# [M] Documenso - Assistant Recipient Can Forge Another Signer's Signature in Sequential-Signing Documents

## Summary
Severity: Medium
Advisory: CVE-2026-71247
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71247
Type: osv

## Details
Documenso's sign-field-with-token.ts, used by the live document-signing UI, allows a recipient with the ASSISTANT role to fetch and complete fields belonging to any later-or-equal-order, not-yet-signed recipient in the same envelope, with no restriction on field type. A newer V2 signing path (sign-envelope-field.ts) explicitly blocks assistants from completing SIGNATURE fields, and the project's own test suite comments confirm this guard is absent from the V1 path used here.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71247.json
- https://github.com/documenso/documenso
- https://nvd.nist.gov/vuln/detail/CVE-2026-71247
