# [H] muhammara and hummus vulnerable to Unchecked Return Value to NULL Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-2r7v-cmch-5x26
CVE: CVE-2022-41957
CWE: CWE-690
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-2r7v-cmch-5x26
Type: github-advisory

## Affected
- npm: `hummus` — affected >=0
- npm: `muhammara` — affected >=3.0.0 <3.4.0
- npm: `muhammara` — affected >=0 <2.6.2

## Details
### Impact
The package muhammara before 2.6.2, from 3.0.0 and before 3.3.0; all versions of package hummus are vulnerable to Denial of Service (DoS) when supplied with a maliciously crafted PDF file to be parsed.

### Patches
It has been patched in 3.4.0 and has been backported to 2.6.2
There is no patch for hummus, currently

### Workarounds
Do not process files from untrusted sources or update.
Replace hummus with muhammara

### References
https://github.com/julianhille/MuhammaraJS/pull/235
https://github.com/julianhille/MuhammaraJS/pull/238

## References
- https://github.com/julianhille/MuhammaraJS/security/advisories/GHSA-2r7v-cmch-5x26
- https://nvd.nist.gov/vuln/detail/CVE-2022-41957
- https://github.com/julianhille/MuhammaraJS/pull/235
- https://github.com/julianhille/MuhammaraJS/pull/238
- https://github.com/julianhille/MuhammaraJS
