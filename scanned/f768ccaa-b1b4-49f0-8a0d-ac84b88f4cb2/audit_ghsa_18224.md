# [H] Mesh Connect JS SDK Vulnerable to Cross Site Scripting via createLink.openLink

## Summary
Severity: High
Advisory: GHSA-vh3f-qppr-j97f
CVE: CVE-2025-59430
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-vh3f-qppr-j97f
Type: github-advisory

## Affected
- npm: `@meshconnect/web-link-sdk` — affected >=0 <3.3.2

## Details
### Summary
The lack of sanitization of URLs protocols in the `createLink.openLink` function enables the execution of arbitrary JavaScript code within the context of the parent page.
### Details
https://github.com/FrontFin/mesh-web-sdk/blob/cf013b85ab95d64c63cbe46d6cb14695474924e7/packages/link/src/Link.ts#L441
The `createLink.openLink` function takes base64 encoded links, decodes them, and then sets the resulting string as the `src` attribute of an `iframe`. It’s important to note that the protocol part is not validated, so a payload, which is a valid URL, such as `javascript:alert(document.domain)//`, can be provided to the function.

### PoC
1. Extract [poc-mesh-web-sdk.zip](https://github.com/user-attachments/files/22223079/poc-mesh-web-sdk.zip)
2. Run `yarn install` and then `yarn start`
3. Paste this payload inside the input box: `amF2YXNjcmlwdDphbGVydCh3aW5kb3cucGFyZW50LmRvY3VtZW50LmJvZHkuZ2V0RWxlbWVudHNCeVRhZ05hbWUoImgyIikuaXRlbSgwKVsiaW5uZXJIVE1MIl0pLy8=` 
4. Click on the _OpenLink_ button
5. Notice the alert box and ability to access the `h2` title from the parent page

It can also be verified via `https://paylink.meshconnect.com/?linkToken=amF2YXNjcmlwdDphbGVydCgpLy8=`.

### Impact
This is technically indistinguishable from a real page at the rendering level and allows access to the parent page DOM, storage, session, and cookies. If the attacker can specify `customIframeId`, they can hijack the source of existing iframes.

If access to the private key is possible or if transactions are tampered with or initialized, in a wallet context, it can result in a critical impact due to loss of funds scenarios.

### Reporters
- [Amine `zwxxb` Elsassi](https://github.com/zwxxb) of [Aptos Labs](https://aptoslabs.com/)

## References
- https://github.com/FrontFin/mesh-web-sdk/security/advisories/GHSA-vh3f-qppr-j97f
- https://nvd.nist.gov/vuln/detail/CVE-2025-59430
- https://github.com/FrontFin/mesh-web-sdk/pull/124
- https://github.com/FrontFin/mesh-web-sdk/commit/7f22148516d58e21a8b7670dde927d614c0d15c2
- https://github.com/FrontFin/mesh-web-sdk
- https://github.com/FrontFin/mesh-web-sdk/blob/cf013b85ab95d64c63cbe46d6cb14695474924e7/packages/link/src/Link.ts#L441
