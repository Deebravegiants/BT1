# [H] Downloads Resources over HTTP in strider-sauce

## Summary
Severity: High
Advisory: GHSA-8gf4-pcj6-54rp
CVE: CVE-2016-10611
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-8gf4-pcj6-54rp
Type: github-advisory

## Affected
- npm: `strider-sauce` — affected >=0

## Details
Affected versions of `strider-sauce` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `strider-sauce`.



## Recommendation

While the package author has created a patch for this vulnerability, they have not yet published it to npm or bumped the version number.

In order to resolve the vulnerability, you will need to install the module manually from github:
```
npm install github:Strider-CD/strider-sauce#5ff6d65
```

As this vulnerability does not have a version bump included with the patch, it is possible that you have received a report for a vulnerable package, yet have installed the patched version and are no longer vulnerable. If that is the case, this advisory can be disregarded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10611
- https://github.com/advisories/GHSA-8gf4-pcj6-54rp
- https://www.npmjs.com/advisories/202
