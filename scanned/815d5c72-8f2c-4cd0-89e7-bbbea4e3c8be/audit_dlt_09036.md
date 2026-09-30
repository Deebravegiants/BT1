# [?] Address CVE-2022-0144, resolve `shelljs` to 0.8.5 (#12927)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-02-14
Source: https://github.com/digital-asset/daml/commit/dc5f2033237c2013688d3f95c5149ef02e235ee8
Type: security-commit

## Details
Address CVE-2022-0144, resolve `shelljs` to 0.8.5 (#12927)

changelog_begin
changelog_end

## Patch
### navigator/frontend/package.json
```diff
@@ -99,6 +99,7 @@
     "**/glob-parent": "^6.0.0",
     "**/set-value": "^4.0.1",
     "**/strip-ansi": "^6.0.0",
+    "**/shelljs": "^0.8.5",
     "modernizr/**/markdown-it": "^12.3.2"
   }
 }
```

### navigator/frontend/yarn.lock
```diff
@@ -6381,10 +6381,10 @@ shebang-regex@^3.0.0:
   resolved "https://registry.yarnpkg.com/shebang-regex/-/shebang-regex-3.0.0.tgz#ae16f1644d873ecad843b0307b143362d4c42172"
   integrity sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==
 
-shelljs@0.8.4:
-  version "0.8.4"
-  resolved "https://registry.yarnpkg.com/shelljs/-/shelljs-0.8.4.tgz#de7684feeb767f8716b326078a8a00875890e3c2"
-  integrity sha512-7gk3UZ9kOfPLIAbslLzyWeGiEqx9e3rxwZM0KE6EL8GlGwjym9Mrlx5/p33bWTu9YG6vcS4MBxYZDHYr5lr8BQ==
+shelljs@0.8.4, shelljs@^0.8.5:
+  version "0.8.5"
+  resolved "https://registry.yarnpkg.com/shelljs/-/shelljs-0.8.5.tgz#de055408d8361bed66c669d2f000538ced8ee20c"
+  integrity sha512-TiwcRcrkhHvbrZbnRcFYMLl30Dfov3HKqzp5tO5b4pt6G/SezKcYhmDg15zXVBswHmctSAQKznqNW2LO5tTDow==
   dependencies:
     glob "^7.0.0"
     interpret "^1.0.0"
```
