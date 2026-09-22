# [M] Sudden swap of user auth tokens in Volto

## Summary
Severity: Medium
Advisory: GHSA-cfhh-xgwq-5r67
CVE: CVE-2022-24740
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-cfhh-xgwq-5r67
Type: github-advisory

## Affected
- npm: `@plone/volto` — affected >=14.0.0-alpha.6 <15.0.0-alpha.0

## Details
### Impact
Due to the usage of an outdated version of the react-cookie library, under the circumstances of given a server high load, it is possible that a user could get his/her auth cookie replaced with the auth cookie from another user, effectively giving him full access to the other users account and privileges. A proven exploit for this vulnerability does not exist, since the exact requisites for it to happen have not been fully clarified, and the attempts to reproduce it under testing conditions have been unsuccessful, but it still can happen randomly and unintentionally in the wild. 

### Patches
The patch and fix is present in Volto 15.0.0-alpha.0 (or later). See PR: https://github.com/plone/volto/pull/3051.
We recommend upgrading to the final release of Volto 15 as soon as possible if running an affected version.
See the upgrade guide https://6-dev-docs.plone.org/volto/upgrade-guide/index.html#upgrading-to-volto-15-x-x

### Workarounds
It is possible to create a fix by manually upgrading the react-cookie package to 4.1.1 and then overriding all Volto components that use this library as in https://github.com/plone/volto/pull/3051. As this is substantial work, an update to the Volto 15 is recommended. The upgrade steps for going from Volto 14 to Volto 15 are quite easy and do not involve any complexity. Please take a look at the upgrade guide: https://6-dev-docs.plone.org/volto/upgrade-guide/index.html#upgrading-to-volto-15-x-x


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [volto](https://github.com/plone/volto/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

## References
- https://github.com/plone/volto/security/advisories/GHSA-cfhh-xgwq-5r67
- https://nvd.nist.gov/vuln/detail/CVE-2022-24740
- https://github.com/plone/volto/pull/3051
- https://github.com/plone/volto
