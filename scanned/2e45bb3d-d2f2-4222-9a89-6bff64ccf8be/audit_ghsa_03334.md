# [H] ApiKey secret could be revelated on network issue

## Summary
Severity: High
Advisory: GHSA-xw22-wv29-3299
CVE: CVE-2021-21421
CWE: CWE-200, CWE-209
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-xw22-wv29-3299
Type: github-advisory

## Affected
- npm: `node-etsy-client` — affected >=0 <0.3.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
Applications that are using node-etsy-client and reporting client error to the end user will offer api key value too

### Patches
_Has the problem been patched? What versions should users upgrade to?_

creharmony/node-etsy-client#18 fixes this issue. This is fixed in [node-etsy-client v0.3.0](https://github.com/creharmony/node-etsy-client/tree/v0.3.0) and later.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Do not report or log etsy client error if you are using version <= v0.2.0

Update your version of node-etsy-client

### References
_Are there any links users can visit to find out more?_

- https://github.com/creharmony/node-etsy-client/issues/17 : On connect error secret appears in error #17

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/creharmony/node-etsy-client/issues](https://github.com/creharmony/node-etsy-client/issues/)

## References
- https://github.com/creharmony/node-etsy-client/security/advisories/GHSA-xw22-wv29-3299
- https://nvd.nist.gov/vuln/detail/CVE-2021-21421
- https://github.com/creharmony/node-etsy-client/commit/b4beb8ef080366c1a87dbf9e163051a446acaa7d
