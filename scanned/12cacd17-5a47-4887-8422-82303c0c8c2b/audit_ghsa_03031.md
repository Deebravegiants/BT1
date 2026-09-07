# [H] Prototype Pollution in Node-Red

## Summary
Severity: High
Advisory: GHSA-xp9c-82x8-7f67
CVE: CVE-2021-21297
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-02-26
Source: https://github.com/advisories/GHSA-xp9c-82x8-7f67
Type: github-advisory

## Affected
- npm: `@node-red/runtime` — affected >=0 <1.2.8

## Details
### Impact

Node-RED 1.2.7 and earlier contains a Prototype Pollution vulnerability in the admin API. A badly formed request can modify the prototype of the default JavaScript Object with the potential to affect the default behaviour of the Node-RED runtime.

### Patches

The vulnerability is patched in the 1.2.8 release.

### Workarounds

A workaround is to ensure only authorised users are able to access the editor url.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@nodered.org](mailto:team@nodered.org)

### Acknowledgements

Thanks to the Tencent Woodpecker Security Team for disclosing this vulnerability.

## References
- https://github.com/node-red/node-red/security/advisories/GHSA-xp9c-82x8-7f67
- https://nvd.nist.gov/vuln/detail/CVE-2021-21297
- https://github.com/node-red/node-red
- https://github.com/node-red/node-red/releases/tag/1.2.8
- https://www.npmjs.com/package/@node-red/editor-api
- https://www.npmjs.com/package/@node-red/runtime
