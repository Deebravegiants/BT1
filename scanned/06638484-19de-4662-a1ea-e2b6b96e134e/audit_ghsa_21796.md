# [C] Prototype Pollution leading to Remote Code Execution in superjson

## Summary
Severity: Critical
Advisory: GHSA-5888-ffcr-r425
CVE: CVE-2022-23631
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-5888-ffcr-r425
Type: github-advisory

## Affected
- npm: `superjson` — affected >=0 <1.8.1
- npm: `blitz` — affected >=0 <0.45.3

## Details
### Impact

This is critical vulnerability, as it allows to run arbitrary code on any server using superjson input, including a Blitz.js server, without prior authentication or knowledge. Attackers gain full control over the server so they could steal and manipulate data or attack further systems. The only requirement is that the server implements at least one endpoint which uses superjson during request processing. In the case of Blitz.js, it would be at least one RPC call. 

### Patches
This has been patched in superjson 1.8.1 and Blitz.js 0.45.3. 

If you are unable to upgrade to Blitz.js 0.45.3 in a timely manner, you can instead upgrade only superjson to version 1.8.1 using yarn resolutions are similar. Blitz versions < 0.45.3 are only affected because they used superjson versions < 1.8.1.

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/blitz-js/superjson
* Email us at b@bayer.ws

### References
* https://www.sonarsource.com/blog/blitzjs-prototype-pollution/

## References
- https://github.com/blitz-js/superjson/security/advisories/GHSA-5888-ffcr-r425
- https://nvd.nist.gov/vuln/detail/CVE-2022-23631
- https://github.com/advisories/GHSA-5888-ffcr-r425
- https://github.com/blitz-js/superjson
- https://www.sonarsource.com/blog/blitzjs-prototype-pollution
