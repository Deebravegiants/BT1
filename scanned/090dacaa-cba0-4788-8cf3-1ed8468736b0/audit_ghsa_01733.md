# [M] CSRF and DNS Rebinding in Oasis

## Summary
Severity: Medium
Advisory: GHSA-j438-45hc-vjhm
CVE: CVE-2020-11003
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-16
Source: https://github.com/advisories/GHSA-j438-45hc-vjhm
Type: github-advisory

## Affected
- npm: `@fraction/oasis` — affected >=0 <2.15.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

If you're running a vulnerable application on your computer and an attacker can trick you into visiting a malicious website, they could use [DNS rebinding](https://en.wikipedia.org/wiki/DNS_rebinding) and [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery) attacks to read/write to vulnerable applications. 

**There is no evidence that suggests that this has been used in the wild.**

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes, 2.15.0.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No.

### References
_Are there any links users can visit to find out more?_

No.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [fraction/oasis](http://github.com/fraction/oasis)
* Email me at [christianbundy@fraction.io](mailto:christianbundy@fraction.io)

## References
- https://github.com/fraction/oasis/security/advisories/GHSA-j438-45hc-vjhm
- https://nvd.nist.gov/vuln/detail/CVE-2020-11003
