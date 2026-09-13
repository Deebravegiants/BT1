# [H] Path Traversal in @backstage/plugin-scaffolder-backend

## Summary
Severity: High
Advisory: GHSA-mg3m-f475-28hv
CVE: CVE-2021-43783
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-mg3m-f475-28hv
Type: github-advisory

## Affected
- npm: `@backstage/plugin-scaffolder-backend` — affected >=0 <0.15.14

## Details
### Impact
A malicious actor with write access to a registered scaffolder template is able to manipulate the template in a way that writes files to arbitrary paths on the scaffolder-backend host instance.

This vulnerability can in some situation also be exploited through user input when executing a template, meaning you do not need write access to the templates. This method will not allow the attacker to control the contents of the injected file however, unless the template is also crafted in a specific way that gives control of the file contents.

### Patches
This vulnerability is fixed in version `0.15.14` of the `@backstage/plugin-scaffolder-backend`.

### Workarounds
This attack is mitigated by restricting access and requiring reviews when registering or modifying scaffolder templates.

### For more information
If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-mg3m-f475-28hv
- https://nvd.nist.gov/vuln/detail/CVE-2021-43783
- https://github.com/backstage/backstage/commit/f9352ab606367cd9efc6ff048915c70ed3013b7f
- https://github.com/backstage/backstage
