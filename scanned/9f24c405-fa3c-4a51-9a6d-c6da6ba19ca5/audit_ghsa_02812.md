# [M] XSS in the `of` option of the `.position()` util in jquery-ui

## Summary
Severity: Medium
Advisory: GHSA-gpqq-952q-5327
CVE: CVE-2021-41184
CWE: CWE-79
Ecosystem: Maven, NuGet, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-10-26
Source: https://github.com/advisories/GHSA-gpqq-952q-5327
Type: github-advisory

## Affected
- npm: `jquery-ui` — affected >=0 <1.13.0
- Maven: `org.webjars.npm:jquery-ui` — affected >=0 <1.13.0
- NuGet: `jQuery.UI.Combined` — affected >=0 <1.13.0
- RubyGems: `jquery-ui-rails` — affected >=0 <7.0.0

## Details
### Impact
Accepting the value of the `of` option of the [`.position()`](https://api.jqueryui.com/position/) util from untrusted sources may execute untrusted code. For example, invoking the following code:
```js
$( "#element" ).position( {
	my: "left top",
	at: "right bottom",
	of: "<img onerror='doEvilThing()' src='/404' />",
	collision: "none"
} );
```
will call the `doEvilThing()` function.

### Patches
The issue is fixed in jQuery UI 1.13.0. Any string value passed to the `of` option is now treated as a CSS selector.

### Workarounds
A workaround is to not accept the value of the `of` option from untrusted sources.

### For more information
If you have any questions or comments about this advisory, search for a relevant issue in [the jQuery UI repo](https://github.com/jquery/jquery-ui/issues). If you don't find an answer, open a new issue.

## References
- https://github.com/jquery/jquery-ui/security/advisories/GHSA-gpqq-952q-5327
- https://nvd.nist.gov/vuln/detail/CVE-2021-41184
- https://github.com/jquery/jquery-ui/commit/effa323f1505f2ce7a324e4f429fa9032c72f280
- https://www.tenable.com/security/tns-2022-09
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.drupal.org/sa-core-2022-001
- https://security.netapp.com/advisory/ntap-20211118-0004
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SNXA7XRKGINWSUIPIZ6ZBCTV6N3KSHES
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SGSY236PYSFYIEBRGDERLA7OSY6D7XL4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O74SXYY7RGXREQDQUDQD4BPJ4QQTD2XQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NXIUUBRVLA4E7G7MMIKCEN75YN7UFERW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HVKIOWSXL2RF2ULNAP7PHESYCFSZIJE3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SNXA7XRKGINWSUIPIZ6ZBCTV6N3KSHES
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SGSY236PYSFYIEBRGDERLA7OSY6D7XL4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O74SXYY7RGXREQDQUDQD4BPJ4QQTD2XQ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NXIUUBRVLA4E7G7MMIKCEN75YN7UFERW
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HVKIOWSXL2RF2ULNAP7PHESYCFSZIJE3
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://github.com/jquery/jquery-ui
