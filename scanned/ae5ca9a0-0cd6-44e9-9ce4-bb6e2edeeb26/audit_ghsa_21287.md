# [H] Signature bypass via multiple root elements

## Summary
Severity: High
Advisory: GHSA-m974-647v-whv7
CVE: CVE-2022-39299
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-m974-647v-whv7
Type: github-advisory

## Affected
- npm: `passport-saml` — affected >=0 <3.2.2
- npm: `node-saml` — affected >=0 <4.0.0-beta.5
- npm: `@node-saml/node-saml` — affected >=0 <4.0.0-beta.5
- npm: `@node-saml/passport-saml` — affected >=0 <4.0.0-beta.3

## Details
### Impact

A remote attacker may be able to bypass SAML authentication on a website using passport-saml. A successful attack requires that the attacker is in possession of an arbitrary IDP signed XML element. Depending on the IDP used, fully unauthenticated attacks (e.g without access to a valid user) might also be feasible if generation of a signed message can be triggered.

### Patches

Users should upgrade to passport-saml 3.2.2 or newer. The issue was also present in the beta releases of `node-saml` before v4.0.0-beta.5.

### Workarounds

Disable SAML authentication.

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open a discussion in the [node-saml repo](https://github.com/node-saml/node-saml/discussions)

### Credits

* Felix Wilhelm of Google Project Zero

## References
- https://github.com/node-saml/passport-saml/security/advisories/GHSA-m974-647v-whv7
- https://nvd.nist.gov/vuln/detail/CVE-2022-39299
- https://github.com/node-saml/passport-saml/commit/8b7e3f5a91c8e5ac7e890a0c90bc7491ce33155e
- https://github.com/node-saml/passport-saml
- https://github.com/node-saml/passport-saml/releases/tag/v3.2.2
- http://packetstormsecurity.com/files/169826/Node-saml-Root-Element-Signature-Bypass.html
