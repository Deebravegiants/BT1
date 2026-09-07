# [M] Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) in sulu/sulu

## Summary
Severity: Medium
Advisory: GHSA-h58v-g3q6-q9fx
CVE: CVE-2021-41169
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-22
Source: https://github.com/advisories/GHSA-h58v-g3q6-q9fx
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=0 <1.6.43

## Details
### Impact

_What kind of vulnerability is it? Who is impacted?_

It is an issue when input HTML into the Tag name. The HTML is execute when the tag name is listed in the auto complete form.
Only admin users are affected and only admin users can create tags.

### Patches

_Has the problem been patched? What versions should users upgrade to?_

The problem is patched with Version 1.6.42.

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Create a custom request listener to avoid that this kind of tags are created.

### References

_Are there any links users can visit to find out more?_

Currently not.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [sulu/sulu repository](https://github.com/sulu/sulu/issues)
* Email us at [security@sulu.io](mailto:security@sulu.io)

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-h58v-g3q6-q9fx
- https://nvd.nist.gov/vuln/detail/CVE-2021-41169
- https://github.com/sulu/sulu/commit/20007ac70a3af3c9e53a6acb0ef8794b65642445
- https://github.com/sulu/sulu
