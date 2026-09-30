# [H] Deskflow - Unauthenticated server-controlled out-of-bounds read in ServerProxy::setOptions / translateKey modifier-table indexing

## Summary
Severity: High
Advisory: CVE-2026-65832
Aliases: GHSA-8rcq-7w87-h64j
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-65832
Type: osv

## Details
Deskflow is a keyboard and mouse sharing app. Prior to continuous build 1.26.0.299, a remote unauthenticated Deskflow server can send kMsgDSetOptions (DSOP) values to ServerProxy::setOptions() in src/lib/client/ServerProxy.cpp so that the value following a modifier option poisons m_modifierTranslationTable, after which ServerProxy::translateKey() or ServerProxy::translateModifierMask() indexes the seven-row s_translationTable or s_masks arrays out of bounds, disclosing four bytes at an attacker-selected relative offset or crashing the connected client; an odd option count also causes an out-of-bounds OptionsList read. This issue is fixed in continuous build 1.26.0.299.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65832.json
- https://github.com/deskflow/deskflow/security/advisories/GHSA-8rcq-7w87-h64j
- https://nvd.nist.gov/vuln/detail/CVE-2026-65832
- https://github.com/deskflow/deskflow/commit/205a3c803e5298d56683660736ec1a41b671b56e
- https://github.com/deskflow/deskflow/commit/8266fbbe6af93fa370018886c7f1f35d2cee8b3f
