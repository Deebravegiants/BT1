# [M] Oceanic allows unsanitized user input to lead to path traversal in URLs

## Summary
Severity: Medium
Advisory: GHSA-5h5v-hw44-f6gg
CVE: CVE-2024-34712
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-5h5v-hw44-f6gg
Type: github-advisory

## Affected
- npm: `oceanic.js` — affected >=0 <1.10.4

## Details
### Impact
Input to functions such as `Client.rest.channels.removeBan` is not url-encoded, resulting in specially crafted input such as `../../../channels/{id}` being normalized into the url `/api/v10/channels/{id}`, and deleting a channel rather than removing a ban.

### Workarounds
* Sanitizing user input, ensuring strings are valid for the purpose they are being used for.
* Encoding input with `encodeURIComponent` before providing it to the library.

### References
OceanicJS/Oceanic@8bf8ee8373b8c565fbdbf70a609aba4fbc1a1ffe

## References
- https://github.com/OceanicJS/Oceanic/security/advisories/GHSA-5h5v-hw44-f6gg
- https://nvd.nist.gov/vuln/detail/CVE-2024-34712
- https://github.com/OceanicJS/Oceanic/commit/8bf8ee8373b8c565fbdbf70a609aba4fbc1a1ffe
- https://github.com/OceanicJS/Oceanic
