# [M] whatsapp-api-js fails to validate message's signature

## Summary
Severity: Medium
Advisory: GHSA-mwhf-vhr5-7j23
CVE: CVE-2024-45607
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-12
Source: https://github.com/advisories/GHSA-mwhf-vhr5-7j23
Type: github-advisory

## Affected
- npm: `whatsapp-api-js` — affected >=4.0.0 <4.0.3

## Details
### Impact
Incorrect Access Control, anyone using the post or verifyRequestSignature methods to handle messages is impacted.

### Patches
Patched in version 4.0.3.

### Workarounds
It's possible to check the payload validation using the WhatsAppAPI.verifyRequestSignature and expect false when the signature is valid.

```ts
function doPost(payload, header_signature) {
    if (whatsapp.verifyRequestSignature(payload.toString(), header_signature) {
        throw 403;
    }
    
    // Now the payload is correctly verified
    whatsapp.post(payload);
}
```

### References
https://github.com/Secreto31126/whatsapp-api-js/pull/371

## References
- https://github.com/Secreto31126/whatsapp-api-js/security/advisories/GHSA-mwhf-vhr5-7j23
- https://nvd.nist.gov/vuln/detail/CVE-2024-45607
- https://github.com/Secreto31126/whatsapp-api-js/pull/371
- https://github.com/Secreto31126/whatsapp-api-js/commit/56620c65126427496a94d176082fbd8393a95b6d
- https://github.com/Secreto31126/whatsapp-api-js
