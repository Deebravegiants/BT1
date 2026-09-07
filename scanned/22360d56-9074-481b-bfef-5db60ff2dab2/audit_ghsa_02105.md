# [H] Processing untrusted theming resources might execute arbitrary code (ACE)

## Summary
Severity: High
Advisory: GHSA-3crj-w4f5-gwh4
CVE: CVE-2021-21316
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-3crj-w4f5-gwh4
Type: github-advisory

## Affected
- npm: `less-openui5` — affected >=0 <0.10.0

## Details
### Impact
When processing theming resources (i.e. `*.less` files) with less-openui5 that originate from an untrusted source, those resources might contain JavaScript code which will be executed in the context of the build process.

While this is a [feature](http://lesscss.org/usage/#less-options-enable-inline-javascript-deprecated-) of the [Less.js library](https://github.com/less/less.js), it is an unexpected behavior in the context of OpenUI5 and SAPUI5 development.

Especially in the context of [UI5 Tooling](https://github.com/SAP/ui5-tooling), which relies on less-openui5, this poses a security threat:

An attacker might create a [library](https://sap.github.io/ui5-tooling/pages/Builder/#library) or [theme-library](https://sap.github.io/ui5-tooling/pages/Builder/#theme-library) containing a custom control or theme, hiding malicious JavaScript code in one of the `.less` files.

This is an example of inline JavaScript in a Less file:
```less
.rule {
	@var: `(function(){console.log('Hello from JavaScript'); process.exit(1);})()`;
	color: @var;
}
```

Starting with Less.js version 3.0.0, the Inline JavaScript feature is disabled by default. less-openui5 however currently uses [a fork](https://github.com/SAP/less-openui5/tree/master/lib/thirdparty/less) of Less.js v1.6.3.

Note that disabling the Inline JavaScript feature in Less.js versions 1.x, still evaluates code has additional double codes around it:
```less
.rule {
	@var: "`(function(){console.log('Hello from JavaScript'); process.exit(1);})()`";
	color: @var;
}
```

### Patches
We decided to remove the inline JavaScript evaluation feature completely from the code of our Less.js fork.

This fix is available in less-openui5 version [v0.10.0](https://github.com/SAP/less-openui5/releases/tag/v0.10.0)

### Workarounds
Only process trusted theming resources.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/SAP/less-openui5
* Email us at secure@sap.com

## References
- https://github.com/SAP/less-openui5/security/advisories/GHSA-3crj-w4f5-gwh4
- https://nvd.nist.gov/vuln/detail/CVE-2021-21316
- https://github.com/SAP/less-openui5/commit/c0d3a8572974a20ea6cee42da11c614a54f100e8
- https://github.com/SAP/less-openui5/releases/tag/v0.10.0
- https://www.npmjs.com/package/less-openui5
- http://lesscss.org/usage/#less-options-enable-inline-javascript-deprecated-
