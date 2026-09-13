# [M] CVE-2021-21259

## Summary
Severity: Medium
Advisory: CVE-2021-21259
Aliases: GHSA-44w9-vm8p-3cxw
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-01-22
Source: https://osv.dev/vulnerability/CVE-2021-21259
Type: osv

## Details
HedgeDoc is open source software which lets you create real-time collaborative markdown notes. In HedgeDoc before version 1.7.2, an attacker can inject arbitrary JavaScript into a HedgeDoc note, which is executed when the note is viewed in slide mode. Depending on the configuration of the instance, the attacker may not need authentication to create or edit notes. The problem is patched in HedgeDoc 1.7.2. As a workaround, disallow loading JavaScript from 3rd party sites using the `Content-Security-Policy` header. Note that this will break some embedded content.

## References
- https://github.com/hedgedoc/hedgedoc/releases/tag/1.7.2
- https://github.com/hedgedoc/hedgedoc/security/advisories/GHSA-44w9-vm8p-3cxw
- https://github.com/hackmdio/codimd/issues/1648
- https://github.com/hedgedoc/hedgedoc/commit/35b0d39a12aa35f27fba8c1f50b1886706e7efef
