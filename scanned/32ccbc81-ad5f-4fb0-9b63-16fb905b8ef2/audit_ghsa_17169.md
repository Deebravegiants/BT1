# [C] JSONata expression can pollute the "Object" prototype

## Summary
Severity: Critical
Advisory: GHSA-fqg8-vfv7-8fj8
CVE: CVE-2024-27307
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-fqg8-vfv7-8fj8
Type: github-advisory

## Affected
- npm: `jsonata` — affected >=1.4.0 <1.8.7
- npm: `jsonata` — affected >=2.0.0 <2.0.4

## Details
### Impact

In JSONata versions `>= 1.4.0, < 1.8.7` and `>= 2.0.0, < 2.0.4`, a malicious expression can use the [transform operator](https://docs.jsonata.org/other-operators#-------transform) to override properties on the `Object` constructor and prototype. This may lead to denial of service, remote code execution or other unexpected behavior in applications that evaluate user-provided JSONata expressions.

### Patch

This issue has been fixed in JSONata versions `>= 1.8.7` and `>= 2.0.4`. Applications that evaluate user-provided expressions should update ASAP to prevent exploitation. The following patch can be applied if updating is not possible.

```patch
--- a/src/jsonata.js
+++ b/src/jsonata.js
@@ -1293,6 +1293,13 @@ var jsonata = (function() {
                 }
                 for(var ii = 0; ii < matches.length; ii++) {
                     var match = matches[ii];
+                    if (match && (match.isPrototypeOf(result) || match instanceof Object.constructor)) {
+                        throw {
+                            code: "D1010",
+                            stack: (new Error()).stack,
+                            position: expr.position
+                        };
+                    }
                     // evaluate the update value for each match
                     var update = await evaluate(expr.update, match, environment);
                     // update must be an object
@@ -1539,7 +1546,7 @@ var jsonata = (function() {
                 if (typeof err.token == 'undefined' && typeof proc.token !== 'undefined') {
                     err.token = proc.token;
                 }
-                err.position = proc.position;
+                err.position = proc.position || err.position;
             }
             throw err;
         }
@@ -1972,6 +1979,7 @@ var jsonata = (function() {
         "T1007": "Attempted to partially apply a non-function. Did you mean ${{{token}}}?",
         "T1008": "Attempted to partially apply a non-function",
         "D1009": "Multiple key definitions evaluate to same key: {{value}}",
+        "D1010": "Attempted to access the Javascript object prototype", // Javascript specific 
         "T1010": "The matcher function argument passed to function {{token}} does not return the correct object structure",
         "T2001": "The left side of the {{token}} operator must evaluate to a number",
         "T2002": "The right side of the {{token}} operator must evaluate to a number",
```

### References

https://github.com/jsonata-js/jsonata/releases/tag/v2.0.4

### Credit

Thank you to Albert Pedersen of Cloudflare for disclosing this issue.

## References
- https://github.com/jsonata-js/jsonata/security/advisories/GHSA-fqg8-vfv7-8fj8
- https://nvd.nist.gov/vuln/detail/CVE-2024-27307
- https://github.com/jsonata-js/jsonata/commit/1d579dbe99c19fbe509f5ba2c6db7959b0d456d1
- https://github.com/jsonata-js/jsonata/commit/335d38f6278e96c908b24183f1c9c90afc8ae00c
- https://github.com/jsonata-js/jsonata/commit/c907b5e517bb718015fcbd993d742ba6202f2be2
- https://github.com/jsonata-js/jsonata
- https://github.com/jsonata-js/jsonata/releases/tag/v2.0.4
