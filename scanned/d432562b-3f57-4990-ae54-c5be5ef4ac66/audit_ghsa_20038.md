# [H] Starcounter-Jack JSON-Patch Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-8gh8-hqwg-xf34
CVE: CVE-2021-4279
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-8gh8-hqwg-xf34
Type: github-advisory

## Affected
- npm: `fast-json-patch` — affected >=0 <3.1.1

## Details
A vulnerability has been found in Starcounter-Jack JSON-Patch up to 3.1.0 and classified as problematic. This vulnerability affects unknown code. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 3.1.1 can address this issue. The name of the patch is 7ad6af41eabb2d799f698740a91284d762c955c9. It is recommended to upgrade the affected component. VDB-216778 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4279
- https://github.com/Starcounter-Jack/JSON-Patch/pull/262
- https://github.com/Starcounter-Jack/JSON-Patch/commit/7ad6af41eabb2d799f698740a91284d762c955c9
- https://blog.effectrenan.com/pwn2win-2021-illusion-web-challenge
- https://github.com/Starcounter-Jack/JSON-Patch
- https://github.com/Starcounter-Jack/JSON-Patch/releases/tag/3.1.1
- https://vuldb.com/?ctiid.216778
- https://vuldb.com/?id.216778
- https://www.huntr.dev/bounties/1-npm-fast-json-patch
