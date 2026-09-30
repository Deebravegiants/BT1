# [?] Address CVE-2022-24785 (#13549)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-04-11
Source: https://github.com/digital-asset/daml/commit/ec87d8dbb115673e9fa0cf079caf4afcdf93c2b1
Type: security-commit

## Details
Address CVE-2022-24785 (#13549)

changelog_begin
changelog_end

## Patch
### navigator/frontend/package.json
```diff
@@ -71,7 +71,7 @@
     "jpeg-js": "^0.4.1",
     "lodash": "^4.17.19",
     "modernizr": "^3.11.8",
-    "moment": "^2.23.0",
+    "moment": "^2.29.2",
     "normalize.css": "^8.0.1",
     "react": "^17.0.1",
     "react-autosuggest": "^10.0.4",
@@ -102,6 +102,7 @@
     "**/shelljs": "^0.8.5",
     "**/minimist": "^1.2.6",
     "**/node-forge": "^1.3.0",
+    "**/moment": "^2.29.2",
     "modernizr/**/markdown-it": "^12.3.2"
   }
 }
```

### navigator/frontend/yarn.lock
```diff
@@ -4944,10 +4944,10 @@ modernizr@^3.11.8:
     requirejs "^2.3.6"
     yargs "^15.4.1"
 
-moment@2.29.1, moment@^2.22.1, moment@^2.23.0:
-  version "2.29.1"
-  resolved "https://registry.yarnpkg.com/moment/-/moment-2.29.1.tgz#b2be769fa31940be9eeea6469c075e35006fa3d3"
-  integrity sha512-kHmoybcPV8Sqy59DwNDY3Jefr64lK/by/da0ViFcuA4DH0vQg5Q6Ze5VimxkfQNSC+Mls/Kx53s7TjP1RhFEDQ==
+moment@2.29.1, moment@^2.22.1, moment@^2.29.2:
+  version "2.29.2"
+  resolved "https://registry.yarnpkg.com/moment/-/moment-2.29.2.tgz#00910c60b20843bcba52d37d58c628b47b1f20e4"
+  integrity sha512-UgzG4rvxYpN15jgCmVJwac49h9ly9NurikMWGPdVxm8GZD6XjkKPxDTjQQ43gtGgnV3X0cAyWDdP2Wexoquifg==
 
 moo@^0.5.0:
   version "0.5.1"
```
