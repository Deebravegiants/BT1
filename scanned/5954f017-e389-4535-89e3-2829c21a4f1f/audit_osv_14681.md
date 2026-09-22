# [C] CVE-2019-10746

## Summary
Severity: Critical
Advisory: CVE-2019-10746
Aliases: GHSA-fhjf-83wg-r2j9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-23
Source: https://osv.dev/vulnerability/CVE-2019-10746
Type: osv

## Details
mixin-deep is vulnerable to Prototype Pollution in versions before 1.3.2 and version 2.0.0. The function mixin-deep could be tricked into adding or modifying properties of Object.prototype using a constructor payload.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BFNIVG2XYFPZJY3DYYBJASZ7ZMKBMIJT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXRA365KZCUNXMU3KDH5JN5BEPNIGUKC/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://snyk.io/vuln/SNYK-JS-MIXINDEEP-450212
