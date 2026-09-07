# [C] plone.app.portlets vulnerable to denial of service via RSS feed portlet

## Summary
Severity: Critical
Advisory: GHSA-x5g3-w747-2h8q
CVE: CVE-2026-55248
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-x5g3-w747-2h8q
Type: github-advisory

## Affected
- PyPI: `plone.app.portlets` — affected >=7.0.0 <7.0.2
- PyPI: `plone.app.portlets` — affected >=6.0.0 <6.0.4
- PyPI: `plone.app.portlets` — affected >=0 <5.0.8

## Details
### Impact
By adding an RSS portlet, and giving this a link to a very large file, a member can cause a denial of service attack, because Plone will use lots of memory. The member could also use different urls to try to get information about the internal network and open port numbers (SSRF). A malicious RSS feed could cause stored XSS, when the url of a feed item is a javascript url.

### Patches
The problem has been patched in `plone.app.portlets`.

* For Plone 6.2: upgrade to `plone.app.portlets` 7.0.2
* For Plone 6.1: upgrade to `plone.app.portlets` 6.0.4
* For Plone 6.0: upgrade to `plone.app.portlets` 5.0.8

### Workarounds
If upgrading is not immediately possible:

- Restrict who can manage portlets: remove the `plone.app.portlets.ManageOwnPortlets` permission from untrusted roles, and limit Manage portlets to trusted administrators (usually this is already restricted to the Manager and Site Administrator roles).
- Where the RSS portlet is not needed, unregister it so it cannot be added. This would need to be done by editing a `portlets.xml` in your own code, so it is not a quick fix.

### References

This is similar to this [`plone.app.event` vulnerability](https://github.com/plone/plone.app.event/security/advisories/GHSA-r82h-mqw3-fc56). It was discovered by the Plone Security Team by thinking of similar cases to the `plone.app.event` problem.

## References
- https://github.com/plone/plone.app.portlets/security/advisories/GHSA-x5g3-w747-2h8q
- https://github.com/plone/plone.app.portlets/commit/09da52ef7b297daa8e0cfd2361e47c37d9b073ad
- https://github.com/plone/plone.app.portlets/commit/9f16b6fb10211916686c6c346ea174bf517e3fbd
- https://github.com/plone/plone.app.portlets/commit/a3b2c2887165b308cd915cbb87b8276f90a76680
- https://github.com/plone/plone.app.portlets/commit/df5e256baee55083cbd6b9a2623675d4cb26b6cd
- https://github.com/plone/plone.app.portlets
