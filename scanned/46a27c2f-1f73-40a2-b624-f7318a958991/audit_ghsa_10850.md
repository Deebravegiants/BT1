# [M] yauzl contains an off-by-one error

## Summary
Severity: Medium
Advisory: GHSA-gmq8-994r-jv83
CVE: CVE-2026-31988
CWE: CWE-193
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-gmq8-994r-jv83
Type: github-advisory

## Affected
- npm: `yauzl` — affected >=3.2.0 <3.2.1

## Details
yauzl (aka Yet Another Unzip Library) version 3.2.0 for Node.js contains an off-by-one error in the NTFS extended timestamp extra field parser within the getLastModDate() function. The while loop condition checks cursor < data.length + 4 instead of cursor + 4 <= data.length, allowing readUInt16LE() to read past the buffer boundary. A remote attacker can cause a denial of service (process crash via ERR_OUT_OF_RANGE exception) by sending a crafted zip file with a malformed NTFS extra field. This affects any Node.js application that processes zip file uploads and calls entry.getLastModDate() on parsed entries. Fixed in version 3.2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31988
- https://github.com/thejoshwolfe/yauzl/commit/c4695215b05c6adffda613b9051a2a85429b33fe
- https://github.com/thejoshwolfe/yauzl
- https://www.codeant.ai/security-research/yauzl-denial-of-service-zip-file-crash
- https://www.npmjs.com/package/yauzl
- https://www.vulncheck.com/advisories/yauzl-denial-of-service-via-off-by-one-error-in-ntfs-timestamp-parser
