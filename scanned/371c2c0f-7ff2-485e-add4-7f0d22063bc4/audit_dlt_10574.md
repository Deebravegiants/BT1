# [?] Merge pull request #632 from libp2p/fix/goprocess-panic

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-05-09
Source: https://github.com/libp2p/go-libp2p/commit/aedbb9caa4dc8fe8d80244deafb8278ae12e6da4
Type: security-commit

## Details
Merge pull request #632 from libp2p/fix/goprocess-panic

dep: update goprocess

## Patch
### go.mod
```diff
@@ -7,7 +7,7 @@ require (
 	github.com/ipfs/go-ipfs-util v0.0.1
 	github.com/ipfs/go-log v0.0.1
 	github.com/jbenet/go-cienv v0.1.0
-	github.com/jbenet/goprocess v0.1.2
+	github.com/jbenet/goprocess v0.1.3
 	github.com/libp2p/go-conn-security v0.0.1
 	github.com/libp2p/go-conn-security-multistream v0.0.2
 	github.com/libp2p/go-libp2p-autonat v0.0.4
```

### go.sum
```diff
@@ -71,8 +71,8 @@ github.com/jbenet/go-temp-err-catcher v0.0.0-20150120210811-aac704a3f4f2 h1:vhC1
 github.com/jbenet/go-temp-err-catcher v0.0.0-20150120210811-aac704a3f4f2/go.mod h1:8GXXJV31xl8whumTzdZsTt3RnUIiPqzkyf7mxToRCMs=
 github.com/jbenet/goprocess v0.0.0-20160826012719-b497e2f366b8 h1:bspPhN+oKYFk5fcGNuQzp6IGzYQSenLEgH3s6jkXrWw=
 github.com/jbenet/goprocess v0.0.0-20160826012719-b497e2f366b8/go.mod h1:Ly/wlsjFq/qrU3Rar62tu1gASgGw6chQbSh/XgIIXCY=
-github.com/jbenet/goprocess v0.1.2 h1:TfvRwwUfgT/umj/REz2B8IxAKzUEX84+xdRAQ+eF2B8=
-github.com/jbenet/goprocess v0.1.2/go.mod h1:5yspPrukOVuOLORacaBi858NqyClJPQxYZlqdZVfqY4=
+github.com/jbenet/goprocess v0.1.3 h1:YKyIEECS/XvcfHtBzxtjBBbWK+MbvA6dG8ASiqwvr10=
+github.com/jbenet/goprocess v0.1.3/go.mod h1:5yspPrukOVuOLORacaBi858NqyClJPQxYZlqdZVfqY4=
 github.com/jessevdk/go-flags v0.0.0-20141203071132-1679536dcc89/go.mod h1:4FA24M0QyGHXBuZZK/XkWh8h0e1EYbRYJSGM75WSRxI=
 github.com/jrick/logrotate v1.0.0/go.mod h1:LNinyqDIJnpAur+b8yyulnQw/wDuN1+BYKlTRt3OuAQ=
 github.com/kisielk/errcheck v1.1.0/go.mod h1:EZBBE59ingxPouuu3KfxchcWSUPOHkagtvWXihfKN4Q=
```
