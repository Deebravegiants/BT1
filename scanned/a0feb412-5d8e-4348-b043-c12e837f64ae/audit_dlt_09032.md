# [?] Address async security advisory (#14595)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-08-03
Source: https://github.com/digital-asset/daml/commit/b1ca1d7aa87978b6c54f08c75cbb5c060a339f10
Type: security-commit

## Details
Address async security advisory (#14595)

- CVE-2021-43138

CHANGELOG_BEGIN
CHANGELOG_END

## Patch
### package.json
```diff
@@ -5,6 +5,9 @@
   "private": true,
   "version": "0.0.0",
   "resolutions": {
+    "grunt/**/async": "^3.2.2",
+    "grunt-browserify/async": "^2.6.4",
+    "grunt-contrib-connect/**/async": "^2.6.4",
     "**/elliptic": "^6.5.4",
     "**/bl": "^4.0.3",
     "grunt-browserify/**/shell-quote": "^1.7.3",
```

### yarn.lock
```diff
@@ -224,19 +224,19 @@ async@^0.9.0:
 async@^1.5.2:
   version "1.5.2"
   resolved "https://registry.yarnpkg.com/async/-/async-1.5.2.tgz#ec6a61ae56480c0c3cb241c95618e20892f9672a"
-  integrity sha1-7GphrlZIDAw8skHJVhjiCJL5Zyo=
+  integrity sha512-nSVgobk4rv61R9PUSDtYt7mPVB2olxNR5RWJcAsH676/ef11bUZwvu7+RGYrYauVdDPcO519v68wRhXQtxsV9w==
 
-async@^2.5.0, async@^2.6.0, async@^2.6.1:
-  version "2.6.3"
-  resolved "https://registry.yarnpkg.com/async/-/async-2.6.3.tgz#d72625e2344a3656e3a3ad4fa749fa83299d82ff"
-  integrity sha512-zflvls11DCy+dQWzTW2dzuilv8Z5X/pjfmZOWba6TNIVDm+2UDaJmXSOXlasHKfNBs8oo3M0aT50fDEWfKZjXg==
+async@^2.5.0, async@^2.6.0, async@^2.6.1, async@^2.6.4:
+  version "2.6.4"
+  resolved "https://registry.yarnpkg.com/async/-/async-2.6.4.tgz#706b7ff6084664cd7eae713f6f965433b5504221"
+  integrity sha512-mzo5dfJYwAn29PeiJ0zvwTo04zj8HDJj0Mn8TD7sno7q12prdbnasKJHhkm2c1LgrhlJ0teaea8860oxi51mGA==
   dependencies:
     lodash "^4.17.14"
 
-async@~3.2.0:
-  version "3.2.0"
-  resolved "https://registry.yarnpkg.com/async/-/async-3.2.0.tgz#b3a2685c5ebb641d3de02d161002c60fc9f85720"
-  integrity sha512-TR2mEZFVOj2pLStYxLht7TyfuRzaydfpxr3k9RpHIzMgw7A64dzsdqCxH1WJyQdoe8T10nDXd9wnEigmiuHIZw==
+async@^3.2.2, async@~3.2.0:
+  version "3.2.4"
+  resolved "https://registry.yarnpkg.com/async/-/async-3.2.4.tgz#2d22e00f8cddeb5fde5dd33522b56d1cf569a81c"
+  integrity sha512-iAB+JbDEGXhyIUavoDl9WP/Jj106Kz9DEn1DPgYw5ruDn0e3Wgi3sKFm55sASdGBNOQB8F59d9qQ7deqrHA8wQ==
 
 available-typed-arrays@^1.0.2:
   version "1.0.4"
```
