# [?] Patched Fix Inefficient Regular Expression Complexity Regular Expression Denial of Service (#4271)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-09-14
Source: https://github.com/iron-fish/ironfish/commit/fe04b02fe6fd5abc916e3715f11a41e6ee4e11bc
Type: security-commit

## Details
Patched Fix Inefficient Regular Expression Complexity Regular Expression Denial of Service (#4271)

Affected of this project are vulnerable to Regular Expression Denial of Service (ReDoS) due to the usage of an insecure regular expression within the result variable.

```js
const wrap = require("word-wrap"); for (let i = 0; i <= 10; i++) { const attack = "a" + "t".repeat(i * 10_00000); const start = performance.now(); wrap( attack, { trim: true }, ); console.log(`${attack.length} characters: ${performance.now() - start}ms`); }
```
Denial of Service (DoS) describes a family of attacks, all aimed at making a system inaccessible to its original and legitimate users. There are many types of DoS attacks, ranging from trying to clog the network pipes to the system by generating a large volume of traffic from many machines (a Distributed Denial of Service - DDoS - attack) to sending crafted requests that cause a system to crash or take a disproportional amount of time to process.

CWE-1333
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

Co-authored-by: jowparks <joe@iflabs.network>
Co-authored-by: Rohan Jadvani <5459049+rohanjadvani@users.noreply.github.com>

## Patch
### yarn.lock
```diff
@@ -11599,9 +11599,9 @@ widest-line@^3.1.0:
     string-width "^4.0.0"
 
 word-wrap@^1.2.3:
-  version "1.2.3"
-  resolved "https://registry.yarnpkg.com/word-wrap/-/word-wrap-1.2.3.tgz#610636f6b1f703891bd34771ccb17fb93b47079c"
-  integrity sha512-Hz/mrNwitNRh/HUAtM/VT/5VH+ygD6DV7mYKZAtHOrbs8U7lvPS6xf7EJKMF0uW1KJCl0H701g3ZGus+muE5vQ==
+  version "1.2.5"
+  resolved "https://registry.yarnpkg.com/word-wrap/-/word-wrap-1.2.5.tgz#d2c45c6dd4fbce621a66f136cbe328afd0410b34"
+  integrity sha512-BN22B5eaMMI9UMtjrGd5g5eCYPpCPDUy0FJXbYsaT5zYxjFOckS53SQDE3pWkVoWpHXVb3BrYcEN4Twa55B5cA==
 
 wordwrap@^1.0.0:
   version "1.0.0"
```
