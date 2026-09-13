# [H] closure-util downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-2hpj-g53m-9gj6
CVE: CVE-2016-10583
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-2hpj-g53m-9gj6
Type: github-advisory

## Affected
- npm: `closure-util` — affected >=0

## Details
Affected versions of `closure-util` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `closure-util`.


## Recommendation

To mitigate this issue:
1. Install the package using npm's `--ignore-scripts` flag.
2. Navigate to the package directory, and open `default-config.json` in a text editor
3. Change the download URLs in the `compiler_url` and `library_url` to `https` equivalents
4. run `npm i` in the package directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10583
- https://github.com/advisories/GHSA-2hpj-g53m-9gj6
- https://www.npmjs.com/advisories/165
