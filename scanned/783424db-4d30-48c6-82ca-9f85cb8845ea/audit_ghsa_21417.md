# [H] muhammara and hummus vulnerable to denial of service by NULL pointer dereference

## Summary
Severity: High
Advisory: GHSA-9cv5-4wqv-9w94
CVE: CVE-2022-25892
CWE: CWE-690
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-9cv5-4wqv-9w94
Type: github-advisory

## Affected
- npm: `muhammara` — affected >=0 <2.6.1
- npm: `muhammara` — affected >=3.0.0 <3.1.1
- npm: `hummus` — affected >=0 <1.0.111

## Details
### Impact
The package muhammara before 2.6.1, from 3.0.0 and before 3.1.1; all versions of package hummus are vulnerable to Denial of Service (DoS) when supplied with a maliciously crafted PDF file to be parsed.

### Patches
It has been patched in 3.1.1 and has been backported to 2.6.1
Hummus has a patch in 1.0.111.

### Workarounds
Do not process files from untrusted sources or update.

### References
https://nvd.nist.gov/vuln/detail/CVE-2022-25892
https://github.com/galkahana/HummusJS/issues/463
https://github.com/julianhille/MuhammaraJS/issues/214
https://github.com/julianhille/MuhammaraJS/commit/1890fb555eaf171db79b73fdc3ea543bbd63c002
https://github.com/julianhille/MuhammaraJS/commit/90b278d09f16062d93a4160ef0a54d449d739c51
https://security.snyk.io/vuln/SNYK-JS-HUMMUS-3091138
https://security.snyk.io/vuln/SNYK-JS-MUHAMMARA-3060320

## References
- https://github.com/julianhille/MuhammaraJS/security/advisories/GHSA-f64j-4x74-p42m
- https://nvd.nist.gov/vuln/detail/CVE-2022-25892
- https://github.com/galkahana/HummusJS/issues/463
- https://github.com/julianhille/MuhammaraJS/issues/214
- https://github.com/galkahana/HummusJS/commit/a9bf2520ab5abb69f9328906e406fbebfb36159a
- https://github.com/julianhille/MuhammaraJS/commit/1890fb555eaf171db79b73fdc3ea543bbd63c002
- https://github.com/julianhille/MuhammaraJS/commit/90b278d09f16062d93a4160ef0a54d449d739c51
- https://github.com/julianhille/MuhammaraJS
- https://security.snyk.io/vuln/SNYK-JS-HUMMUS-3091138
- https://security.snyk.io/vuln/SNYK-JS-MUHAMMARA-3060320
