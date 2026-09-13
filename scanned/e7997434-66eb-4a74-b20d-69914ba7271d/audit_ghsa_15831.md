# [M] Butterfly's parseJSON, getJSON functions eval malicious input, leading to remote code execution (RCE)

## Summary
Severity: Medium
Advisory: GHSA-mpcw-3j5p-p99x
CWE: CWE-185, CWE-95
Ecosystem: Maven
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-mpcw-3j5p-p99x
Type: github-advisory

## Affected
- Maven: `org.openrefine.dependencies:butterfly` — affected >=0 <1.2.6

## Details
### Summary

Usage of the `Butterfly.prototype.parseJSON` or `getJSON` functions on an attacker-controlled crafted input string allows the attacker to execute arbitrary JavaScript code on the server.

Since Butterfly JavaScript code has access to Java classes, it can run arbitrary programs.

### Details

The `parseJSON` function (edu/mit/simile/butterfly/Butterfly.js:64) works by calling `eval`, an approach that goes back to the original library by Crockford, before JSON was part of the ECMAScript language. It uses a regular expression to remove strings from the input, then checks that there are no unexpected characters in the non-string remainder.

However, the regex is imperfect, as was [discovered earlier by Mike Samuel](https://dev.to/mikesamuel/2008-silently-securing-jsonparse-5cbb); specifically, the "cleaner" can be tricked into treating part of the input as a string that the "evaluator" does not, because of a difference in interpretation regarding the [the Unicode zero-width joiner character](https://unicode-explorer.com/c/200D). Representing that character with a visible symbol, a malicious input looks like:

```js
"\�\", Packages.java.lang.Runtime.getRuntime().exec('gnome-calculator')) // "
```

This is understood...

* by `JSON_cleaning_RE` as a single string, and because it is a string it can be collapsed to nothing, which is not problematic, so the original input proceeds to `eval`.
* by the `eval` function, which ignores zero-width joiners entirely, as a string containing a single escaped backslash, followed by a comma, then a function call, closing parenthesis, and finally a line comment.
 
The function call is evaluated, and a calculator is opened.

Possible mitigations and additional defenses could include:

* Replacing the JSON implementation with Rhino's built-in implementation.
* Dropping all JSON-related and JSONP-related code entirely.
* Restricting the access the JavaScript controller code has to the rest of the system by using `initSafeStandardObjects` instead of `initStandardObjects`, using `setClassShutter`, and so on.

### PoC

Change OpenRefine `core` `controller.js` to add a call to the vulnerable `getJSON` function:

```diff
diff --git a/main/webapp/modules/core/MOD-INF/controller.js b/main/webapp/modules/core/MOD-INF/controller.js
index 4ceba0676..1ce0936d2 100644
--- a/main/webapp/modules/core/MOD-INF/controller.js
+++ b/main/webapp/modules/core/MOD-INF/controller.js
@@ -631,0 +632,5 @@ function process(path, request, response) {
+    if (path == "getjsontest") {
+      butterfly.getJSON(request);
+      return true;
+    }
+
```

Then, restart OpenRefine and submit the malicious request. For example, the following `bash` command (with $' quoting) should do it:

```
curl -H 'Content-Type: application/json;charset=utf-8' --data $'"\\\u200d\\", Packages.java.lang.Runtime.getRuntime().exec(\'gnome-calculator\')) // "' http://localhost:3333/getjsontest
```

### Impact

Any JavaScript controller that calls one of these functions is vulnerable to remote code execution.

OpenRefine itself seems unaffected; both OpenRefine and jQuery have their own functions also called parseJSON and getJSON, but those are unrelated.

## References
- https://github.com/OpenRefine/simile-butterfly/security/advisories/GHSA-mpcw-3j5p-p99x
- https://github.com/OpenRefine/simile-butterfly/commit/2ad1fa4cd8afe3c920c8e6e04fe7a7df5cf8294e
- https://github.com/OpenRefine/simile-butterfly
