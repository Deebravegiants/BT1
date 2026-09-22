# [C] Changeset vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-2gqw-q9r9-7f79
CVE: CVE-2021-25915
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2gqw-q9r9-7f79
Type: github-advisory

## Affected
- npm: `changeset` — affected >=0.0.1 <0.2.5

## Details
### Overview
Prototype pollution vulnerability in 'changeset' versions 0.0.1 through 0.2.5 allows attackers to cause a denial of service and may lead to remote code execution.

### Details
The npm module 'changeset' can be abused by Prototype Pollution vulnerability since the function 'apply()' does not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC Details
The 'apply()' function accepts 'changes, target, modify' as argument. Due to the absence of validation on the values passed into the 'changes' argument, an attacker can supply a malicious value by adjusting the value to include the '__proto__' property. Since there is no validation before assigning the property to check whether the assigned argument is the Object's own property or not, the property 'polluted' will be directly be assigned to the new object thereby polluting the Object prototype. Using the example below, if there is a check to validate 'polluted' the valued later in the code, it would be substituted as "Yes! Its Polluted" as it had been polluted.

### PoC Code

```js
var changeset = require("changeset") const patch = [{
    type: 'put',
    key: ["__proto__", "polluted"],
    value: "Yes! Its Polluted"
}];
console.log("Before : " + {}.polluted);
changeset.apply(patch, {}, true);
console.log("After : " + {}.polluted);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25915
- https://github.com/eugeneware/changeset/commit/9e588844edbb9993b32e7366cc799262b4447f99
- https://github.com/eugeneware/changeset
- https://web.archive.org/web/20210323102946/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25915
