# [M] XSS in dojox due to insufficient escape in dojox.xmpp.util.xmlEncode 

## Summary
Severity: Medium
Advisory: GHSA-pg97-ww7h-5mjr
CVE: CVE-2019-10785
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-02-13
Source: https://github.com/advisories/GHSA-pg97-ww7h-5mjr
Type: github-advisory

## Affected
- npm: `dojox` — affected >=0 <1.11.9
- npm: `dojox` — affected >=1.12.0 <1.12.7
- npm: `dojox` — affected >=1.13.0 <1.13.6
- npm: `dojox` — affected >=1.14.0 <1.14.5
- npm: `dojox` — affected >=1.15.0 <1.15.2
- npm: `dojox` — affected >=1.16.0 <1.16.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Potential XSS vulnerability for users of `dojox/xmpp` and `dojox/dtl`.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes, patches are available for the 1.11 through 1.16 versions. Users should upgrade to one of these versions of Dojo:

* 1.16.1
* 1.15.2
* 1.14.5
* 1.13.6
* 1.12.7
* 1.11.9

Users of Dojo 1.10.x and earlier should review this change and determine if it impacts them, and backport the change as appropriate.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The change applied in https://github.com/dojo/dojox/pull/315 could get added separately as a patch.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [dojo/dojox](https://github.com/dojo/dojox/)

## References
- https://github.com/dojo/dojox/security/advisories/GHSA-pg97-ww7h-5mjr
- https://nvd.nist.gov/vuln/detail/CVE-2019-10785
- https://github.com/dojo/dojox/pull/315
- https://github.com/dojo/dojox/commit/abd033a787c718abc1a390f480ac3ea61288e5ee
- https://lists.debian.org/debian-lts-announce/2020/02/msg00033.html
- https://snyk.io/vuln/SNYK-JS-DOJOX-548257
- https://snyk.io/vuln/SNYK-JS-DOJOX-548257,
