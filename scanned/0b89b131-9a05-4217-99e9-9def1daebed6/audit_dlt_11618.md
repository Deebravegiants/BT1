# [?] Problem: ReadUpgradeInfoFromDisk cause panic on startup occasionally (fixes #589) (#595)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2021-07-12
Source: https://github.com/crypto-org-chain/chain-main/commit/63f9a7a0e35e3bf703b0bb10e71193a0cb905da1
Type: security-commit

## Details
Problem: ReadUpgradeInfoFromDisk cause panic on startup occasionally (fixes #589) (#595)

Solution: bumped SDK version to v0.42.7 which backported the fix

## Patch
### CHANGELOG.md
```diff
@@ -1,5 +1,10 @@
 # Changelog
 
+*July 12, 2021*
+
+## v2.1.1
+This version is based on Cosmos SDK 0.42.7 which, among other changes, contains additional state sync-related fixes.
+
 *June 22, 2021*
 
 ## v2.1.0
```

### go.mod
```diff
@@ -4,7 +4,7 @@ go 1.16
 
 require (
 	github.com/confluentinc/bincover v0.1.0
-	github.com/cosmos/cosmos-sdk v0.42.6
+	github.com/cosmos/cosmos-sdk v0.42.7
 	github.com/cosmos/ledger-go v0.9.2 // indirect
 	github.com/gogo/protobuf v1.3.3
 	github.com/golang/protobuf v1.5.2
@@ -33,6 +33,6 @@ replace github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alp
 replace github.com/cosmos/ledger-cosmos-go => github.com/crypto-com/ledger-cosmos-go v0.9.10-0.20200929055312-01e1d341de0f
 
 // TODO: fix keyring upstream
-replace github.com/99designs/keyring => github.com/crypto-org-chain/keyring v1.1.6-gnome
+replace github.com/99designs/keyring => github.com/crypto-org-chain/keyring v1.1.6-fixes
 
 replace github.com/dgrijalva/jwt-go => github.com/dgrijalva/jwt-go/v4 v4.0.0-preview1
```

### go.sum
```diff
@@ -99,8 +99,8 @@ github.com/coreos/go-systemd v0.0.0-20180511133405-39ca1b05acc7/go.mod h1:F5haX7
 github.com/coreos/go-systemd v0.0.0-20190321100706-95778dfbb74e/go.mod h1:F5haX7vjVVG0kc13fIWeqUViNPyEJxv/OmvnBo0Yme4=
 github.com/coreos/pkg v0.0.0-20160727233714-3ac0863d7acf/go.mod h1:E3G3o1h8I7cfcXa63jLwjI0eiQQMgzzUDFVpN/nH/eA=
 github.com/coreos/pkg v0.0.0-20180928190104-399ea9e2e55f/go.mod h1:E3G3o1h8I7cfcXa63jLwjI0eiQQMgzzUDFVpN/nH/eA=
-github.com/cosmos/cosmos-sdk v0.42.6 h1:ps1QWfvaX6VLNcykA7wzfii/5IwBfYgTIik6NOVDq/c=
-github.com/cosmos/cosmos-sdk v0.42.6/go.mod h1:kh37gwYQoWdgR7N/9zeqW2rJ7cnP2W4A7nqIaf6m3zg=
+github.com/cosmos/cosmos-sdk v0.42.7 h1:f+ZUjao2y93I37RZ7P2d94JdcEsS7Vq64SBLcNITAVc=
+github.com/cosmos/cosmos-sdk v0.42.7/go.mod h1:SrclJP9lMXxz2fCbngxb0brsPNuZXqoQQ9VHuQ3Tpf4=
 github.com/cosmos/go-bip39 v0.0.0-20180819234021-555e2067c45d/go.mod h1:tSxLoYXyBmiFeKpvmq4dzayMdCjCnu8uqmCysIGBT2Y=
 github.com/cosmos/go-bip39 v1.0.0 h1:pcomnQdrdH22njcAatO0yWojsUnCO3y2tNoV1cb6hHY=
 github.com/cosmos/go-bip39 v1.0.0/go.mod h1:RNJv0H/pOIVgxw6KS7QeX2a0Uo0aKUlfhZ4xuwvCdJw=
@@ -117,8 +117,8 @@ github.com/cpuguy83/go-md2man/v2 v2.0.0/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsr
 github.com/creack/pty v1.1.7/go.mod h1:lj5s0c3V2DBrqTV7llrYr5NG6My20zk30Fl46Y7DoTY=
 github.com/crypto-com/ledger-cosmos-go v0.9.10-0.20200929055312-01e1d341de0f h1:pizxWsDWb07eC9jhw1oEUraFSZr3q17jvBU8CZ5Cp6s=
 github.com/crypto-com/ledger-cosmos-go v0.9.10-0.20200929055312-01e1d341de0f/go.mod h1:TJ0bt9M3eOD5V6ZCUvenKA1ODkvOcYuJDMBr9/XW1QY=
-github.com/crypto-org-chain/keyring v1.1.6-gnome h1:Gnro7SoBk+Lma9uNA67xKAeu/WdqtZTH91GP8HbPAKw=
-github.com/crypto-org-chain/keyring v1.1.6-gnome/go.mod h1:0mkLWIoZuQ7uBoospo5Q9zIpqq6rYCPJDSUdeCJvPM8=
+github.com/crypto-org-chain/keyring v1.1.6-fixes h1:AUFSu56NY6XobY6XfRoDx6v3loiOrHK5MNUm32GEjwA=
+github.com/crypto-org-chain/keyring v1.1.6-fixes/go.mod h1:0mkLWIoZuQ7uBoospo5Q9zIpqq6rYCPJDSUdeCJvPM8=
 github.com/danieljoos/wincred v1.0.2 h1:zf4bhty2iLuwgjgpraD2E9UbvO+fe54XXGJbOwe23fU=
 github.com/danieljoos/wincred v1.0.2/go.mod h1:SnuYRW9lp1oJrZX/dXJqr0cPK5gYXqx3EJbmjhLdK9U=
 github.com/davecgh/go-spew v0.0.0-20171005155431-ecdeabc65495/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
```

### gomod2nix.toml
```diff
@@ -60,13 +60,13 @@
     sha256 = "1isd03hgiwcf2ld1rlp0plrnfz7r4i7c5q4kb6hkcd22axnmrv0z"
 
 ["github.com/99designs/keyring"]
-  sumVersion = "v1.1.6-gnome"
+  sumVersion = "v1.1.6-fixes"
   vendorPath = "github.com/crypto-org-chain/keyring"
   ["github.com/99designs/keyring".fetch]
     type = "git"
     url = "https://github.com/crypto-org-chain/keyring"
-    rev = "0cfb890bbc9a5787491322a75c76b906165cb816"
-    sha256 = "1di3g22jihr25i6l7svc8r0mfvilck79rk3i88df627pihj64gsf"
+    rev = "4fc1291852fc269b98e8466bfa8f0ce9b8e665ad"
+    sha256 = "1c55z0hhvk8w1mfwc587yd88hiyi6bnpnbd3p9dckj9sx8pw4rvi"
 
 ["github.com/BurntSushi/toml"]
   sumVersion = "v0.3.1"
@@ -511,12 +511,12 @@
     sha256 = "0nxbn0m7lr4dg0yrwnvlkfiyg3ndv8vdpssjx7b714nivpc6ar0y"
 
 ["github.com/cosmos/cosmos-sdk"]
-  sumVersion = "v0.42.6"
+  sumVersion = "v0.42.7"
   ["github.com/cosmos/cosmos-sdk".fetch]
     type = "git"
     url = "https://github.com/cosmos/cosmos-sdk"
-    rev = "a7e19ad4588bcceeeeab522f5807b9ff22e91a8c"
-    sha256 = "1ysk7bqivhg5d3dcgksl91jmcc3nakvfkgfiry408v66vk8hbpx6"
+    rev = "84c33215658131d87daf3c629e909e12ed9370fa"
+    sha256 = "1pqb3m3bsmxs6j0cx4d48jnsxkx9hpki30w13q7wckz21pljwi3q"
 
 ["github.com/cosmos/go-bip39"]
   sumVersion = "v1.0.0"
```

### third_party/cosmos-sdk
```diff
@@ -1 +1 @@
-Subproject commit a7e19ad4588bcceeeeab522f5807b9ff22e91a8c
+Subproject commit 84c33215658131d87daf3c629e909e12ed9370fa
```
