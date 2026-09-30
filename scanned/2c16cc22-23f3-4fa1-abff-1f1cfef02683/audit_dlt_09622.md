# [?] Problem: authz module has security vulnerability (#167)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2021-10-13
Source: https://github.com/crypto-org-chain/cronos/commit/86ebb2b4d2c4d833f52b65ef0e8bec1e95582764
Type: security-commit

## Details
Problem: authz module has security vulnerability (#167)

Solution:
- update cosmos-sdk to 0.44.2

use replace

## Patch
### CHANGELOG.md
```diff
@@ -6,6 +6,7 @@
 - [cronos#144](https://github.com/crypto-org-chain/cronos/pull/144) fix events in autodeploy crc20 module contract
 - [gravity-bridge#17](https://github.com/crypto-org-chain/gravity-bridge/pull/17) processEthereumEvent does not persist hooks emitted event
 - [gravity-bridge#20](https://github.com/crypto-org-chain/gravity-bridge/pull/20) fix undeterministic in consensus
+- [cronos#167](https://github.com/crypto-org-chain/cronos/pull/167) upgrade cosmos-sdk to 0.44.2
 
 ### Improvements
 - [cronos#162](https://github.com/crypto-org-chain/cronos/pull/162) bump ibc-go to v1.2.1 with hooks support
```

### go.mod
```diff
@@ -4,7 +4,7 @@ go 1.16
 
 require (
 	github.com/armon/go-metrics v0.3.9
-	github.com/cosmos/cosmos-sdk v0.44.1
+	github.com/cosmos/cosmos-sdk v0.44.2
 	github.com/cosmos/ibc-go v1.2.1
 	github.com/ethereum/go-ethereum v1.10.3
 	github.com/gogo/protobuf v1.3.3
@@ -42,3 +42,6 @@ replace github.com/peggyjv/gravity-bridge/module => github.com/crypto-org-chain/
 replace github.com/cosmos/iavl => github.com/cosmos/iavl v0.17.1
 
 replace github.com/ethereum/go-ethereum => github.com/crypto-org-chain/go-ethereum v1.10.3-patched
+
+// TODO: remove when ibc-go and ethermint upgrades cosmos-sdk
+replace github.com/cosmos/cosmos-sdk => github.com/cosmos/cosmos-sdk v0.44.2
```

### go.sum
```diff
@@ -245,8 +245,8 @@ github.com/coreos/go-systemd v0.0.0-20190620071333-e64a0ec8b42a/go.mod h1:F5haX7
 github.com/coreos/go-systemd/v22 v22.3.2/go.mod h1:Y58oyj3AT4RCenI/lSvhwexgC+NSVTIJ3seZv2GcEnc=
 github.com/coreos/pkg v0.0.0-20160727233714-3ac0863d7acf/go.mod h1:E3G3o1h8I7cfcXa63jLwjI0eiQQMgzzUDFVpN/nH/eA=
 github.com/coreos/pkg v0.0.0-20180928190104-399ea9e2e55f/go.mod h1:E3G3o1h8I7cfcXa63jLwjI0eiQQMgzzUDFVpN/nH/eA=
-github.com/cosmos/cosmos-sdk v0.44.1 h1:UspmTMwKNGf6mH8k388v2T5csP9BYpPJkbQ/eG30PtM=
-github.com/cosmos/cosmos-sdk v0.44.1/go.mod h1:fwQJdw+aECatpTvQTo1tSfHEsxACdZYU80QCZUPnHr4=
+github.com/cosmos/cosmos-sdk v0.44.2 h1:EWoj9h9Q9t7uqS3LyqzZWWwnSEodUJlYDMloDoPBD3Y=
+github.com/cosmos/cosmos-sdk v0.44.2/go.mod h1:fwQJdw+aECatpTvQTo1tSfHEsxACdZYU80QCZUPnHr4=
 github.com/cosmos/go-bip39 v0.0.0-20180819234021-555e2067c45d/go.mod h1:tSxLoYXyBmiFeKpvmq4dzayMdCjCnu8uqmCysIGBT2Y=
 github.com/cosmos/go-bip39 v1.0.0 h1:pcomnQdrdH22njcAatO0yWojsUnCO3y2tNoV1cb6hHY=
 github.com/cosmos/go-bip39 v1.0.0/go.mod h1:RNJv0H/pOIVgxw6KS7QeX2a0Uo0aKUlfhZ4xuwvCdJw=
```

### gomod2nix.toml
```diff
@@ -1103,12 +1103,12 @@
     sha256 = "0nxbn0m7lr4dg0yrwnvlkfiyg3ndv8vdpssjx7b714nivpc6ar0y"
 
 ["github.com/cosmos/cosmos-sdk"]
-  sumVersion = "v0.44.1"
+  sumVersion = "v0.44.2"
   ["github.com/cosmos/cosmos-sdk".fetch]
     type = "git"
     url = "https://github.com/cosmos/cosmos-sdk"
-    rev = "8a73b266f52e08f24738c93ef519b529cd35bbd8"
-    sha256 = "1d95issqzyksh8zyyi7b7px00fv7xfyg2xz2nk6dms4kq6g9y7fb"
+    rev = "68ab790a761e80d3674f821794cf18ccbfed45ee"
+    sha256 = "13rkaadk0kp3n9xyfaffqs3sh7n017nl9s2pca6i3hdf6h8s03a0"
 
 ["github.com/cosmos/go-bip39"]
   sumVersion = "v1.0.0"
```
