# [H] Remote Code Execution in Angular Expressions

## Summary
Severity: High
Advisory: GHSA-hxhm-96pp-2m43
CVE: CVE-2020-5219
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-01-24
Source: https://github.com/advisories/GHSA-hxhm-96pp-2m43
Type: github-advisory

## Affected
- npm: `angular-expressions` — affected >=0 <1.0.1

## Details
### Impact

The vulnerability, reported by GoSecure Inc, allows Remote Code Execution, if you call `expressions.compile(userControlledInput)` where `userControlledInput` is text that comes from user input.

* If running angular-expressions in the browser, an attacker could run any browser script when the application code calls expressions.compile(userControlledInput).
* If running angular-expressions on the server, an attacker could run any Javascript expression, thus gaining Remote Code Execution.

### Patches

Users should upgrade to version 1.0.1 of angular-expressions

### Workarounds

A temporary workaround might be either to : 

* disable user-controlled input that will be fed into angular-expressions in your application

OR

* allow only following characters in the userControlledInput : 

```js
if (/^[|a-zA-Z.0-9 :"'+-?]+$/.test(userControlledInput)) {
      var result = expressions.compile(userControlledInput);
}
else {
     result = undefined;
}
```

### References

[Removal of angular-expression sandbox](http://blog.angularjs.org/2016/09/angular-16-expression-sandbox-removal.html)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [angular-expressions](https://github.com/peerigon/angular-expressions/issues)
* [Email us](mailto:contact@javascript-ninja.fr)

### Credits 

The issue was reported by Maxime Nadeau from GoSecure, Inc.

## References
- https://github.com/peerigon/angular-expressions/security/advisories/GHSA-hxhm-96pp-2m43
- https://nvd.nist.gov/vuln/detail/CVE-2020-5219
- https://github.com/peerigon/angular-expressions/commit/061addfb9a9e932a970e5fcb913d020038e65667
- http://blog.angularjs.org/2016/09/angular-16-expression-sandbox-removal.html
