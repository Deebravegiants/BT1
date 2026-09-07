# [H] msgpackr's conversion of property names to strings can trigger infinite recursion

## Summary
Severity: High
Advisory: GHSA-7hpj-7hhx-2fgx
CVE: CVE-2023-52079
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-7hpj-7hhx-2fgx
Type: github-advisory

## Affected
- npm: `msgpackr` — affected >=0 <1.10.1

## Details
### Impact
When decoding user supplied MessagePack messages, users can trigger stuck threads by crafting messages that keep the decoder stuck in a loop.

### Patches
The fix is available in v1.10.1

### Workarounds
Exploits seem to require structured cloning, replacing the 0x70 extension with your own (that throws an error or does something other than recursive referencing) should mitigate the issue.

### References

## References
- https://github.com/kriszyp/msgpackr/security/advisories/GHSA-7hpj-7hhx-2fgx
- https://nvd.nist.gov/vuln/detail/CVE-2023-52079
- https://github.com/kriszyp/msgpackr/commit/18f44f8800e2261341cdf489d1ba1e35a0133602
- https://github.com/kriszyp/msgpackr
