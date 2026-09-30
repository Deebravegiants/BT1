# [?] cmd/geth: implement vulnerability check (#21859)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-12-04
Source: https://github.com/celo-org/celo-blockchain/commit/15339cf1c9af2b1242c2574869fa7afca1096cdf
Type: security-commit

## Details
cmd/geth: implement vulnerability check (#21859)

* cmd/geth: implement vulnerability check

* cmd/geth: use minisign to verify vulnerability feed

* cmd/geth: add the test too

* cmd/geth: more minisig/signify testing

* cmd/geth: support multiple pubfiles for signing

* cmd/geth: add @holiman minisig pubkey

* cmd/geth: polishes on vulnerability check

* cmd/geth: fix ineffassign linter nit

* cmd/geth: add CVE to version check struct

* cmd/geth/testdata: add missing testfile

* cmd/geth: add more keys to versionchecker

* cmd/geth: support file:// URLs in version check

* cmd/geth: improve key ID printing when signature check fails

Co-authored-by: Felix Lange <fjl@twurst.com>

## Patch
### cmd/geth/main.go
```diff
@@ -242,6 +242,7 @@ func init() {
 		makecacheCommand,
 		makedagCommand,
 		versionCommand,
+		versionCheckCommand,
 		licenseCommand,
 		// See config.go
 		dumpConfigCommand,
```

### cmd/geth/misccmd.go
```diff
@@ -31,6 +31,18 @@ import (
 )
 
 var (
+	VersionCheckUrlFlag = cli.StringFlag{
+		Name:  "check.url",
+		Usage: "URL to use when checking vulnerabilities",
+		Value: "https://geth.ethereum.org/docs/vulnerabilities/vulnerabilities.json",
+	}
+	VersionCheckVersionFlag = cli.StringFlag{
+		Name:  "check.version",
+		Usage: "Version to check",
+		Value: fmt.Sprintf("Geth/v%v/%v-%v/%v",
+			params.VersionWithCommit(gitCommit, gitDate),
+			runtime.GOOS, runtime.GOARCH, runtime.Version()),
+	}
 	makecacheCommand = cli.Command{
 		Action:    utils.MigrateFlags(makecache),
 		Name:      "makecache",
@@ -65,6 +77,21 @@ Regular users do not need to execute it.
 		Category:  "MISCELLANEOUS COMMANDS",
 		Description: `
 The output of this command is supposed to be machine-readable.
+`,
+	}
+	versionCheckCommand = cli.Command{
+		Action: utils.MigrateFlags(versionCheck),
+		Flags: []cli.Flag{
+			VersionCheckUrlFlag,
+			VersionCheckVersionFlag,
+		},
+		Name:      "version-check",
+		Usage:     "Checks (online) whether the current version suffers from any known security vulnerabilities",
+		ArgsUsage: "<versionstring (optional)>",
+		Category:  "MISCELLANEOUS COMMANDS",
+		Description: `
+The version-check command fetches vulnerability-information from https://geth.ethereum.org/docs/vulnerabilities/vulnerabilities.json, 
+and displays information about any security vulnerabilities that affect the currently executing version.
 `,
 	}
 	licenseCommand = cli.Command{
```

### cmd/geth/testdata/vcheck/data.json
```diff
@@ -0,0 +1,61 @@
+[
+  {
+    "name": "CorruptedDAG",
+    "uid": "GETH-2020-01",
+    "summary": "Mining nodes will generate erroneous PoW on epochs > `385`.",
+    "description": "A mining flaw could cause miners to erroneously calculate PoW, due to an index overflow, if DAG size is exceeding the maximum 32 bit unsigned value.\n\nThis occurred on the ETC chain on 2020-11-06. This is likely to trigger for ETH mainnet around block `11550000`/epoch `385`, slated to occur early January 2021.\n\nThis issue is relevant only for miners, non-mining nodes are unaffected, since non-mining nodes use a smaller verification cache instead of a full DAG.",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/pull/21793",
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/",
+      "https://github.com/ethereum/go-ethereum/commit/567d41d9363706b4b13ce0903804e8acf214af49"
+    ],
+    "introduced": "v1.6.0",
+    "fixed": "v1.9.24",
+    "published": "2020-11-12",
+    "severity": "Medium",
+    "check": "Geth\\/v1\\.(6|7|8)\\..*|Geth\\/v1\\.9\\.2(1|2|3)-.*"
+  },
+  {
+    "name": "GoCrash",
+    "uid": "GETH-2020-02",
+    "summary": "A denial-of-service issue can be used to crash Geth nodes during block processing, due to an underlying bug in Go (CVE-2020-28362) versions < `1.15.5`, or `<1.14.12`",
+    "description": "The DoS issue can be used to crash all Geth nodes during block processing, the effects of which would be that a major part of the Ethereum network went offline.\n\nOutside of Go-Ethereum, the issue is most likely relevant for all forks of Geth (such as TurboGeth or ETC’s core-geth) which is built with versions of Go which contains the vulnerability.",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/",
+      "https://groups.google.com/g/golang-announce/c/NpBGTTmKzpM",
+      "https://github.com/golang/go/issues/42552"
+    ],
+    "fixed": "v1.9.24",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth.*\\/go1\\.(11(.*)|12(.*)|13(.*)|14|14\\.(\\d|10|11|)|15|15\\.[0-4])$"
+  },
+  {
+    "name": "ShallowCopy",
+    "uid": "GETH-2020-03",
+    "summary": "A consensus flaw in Geth, related to `datacopy` precompile",
+    "description": "Geth erroneously performed a 'shallow' copy when the precompiled `datacopy` (at `0x00...04`) was invoked. An attacker could deploy a contract that uses the shallow copy to corrupt the contents of the `RETURNDATA`, thus causing a consensus failure.",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/"
+    ],
+    "introduced": "v1.9.7",
+    "fixed": "v1.9.17",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth\\/v1\\.9\\.(7|8|9|10|11|12|13|14|15|16).*$"
+  },
+  {
+    "name": "GethCrash",
+    "uid": "GETH-2020-04",
+    "summary": "A denial-of-service issue can be used to crash Geth nodes during block processing",
+    "description": "Full details to be disclosed at a later date",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/"
+    ],
+    "introduced": "v1.9.16",
+    "fixed": "v1.9.18",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth\\/v1\\.9.(16|17).*$"
+  }
+]
```

### cmd/geth/testdata/vcheck/data2.json
```diff
@@ -0,0 +1,62 @@
+[
+  {
+    "name": "CorruptedDAG",
+    "uid": "GETH-2020-01",
+    "summary": "Mining nodes will generate erroneous PoW on epochs > `385`.",
+    "description": "A mining flaw could cause miners to erroneously calculate PoW, due to an index overflow, if DAG size is exceeding the maximum 32 bit unsigned value.\n\nThis occurred on the ETC chain on 2020-11-06. This is likely to trigger for ETH mainnet around block `11550000`/epoch `385`, slated to occur early January 2021.\n\nThis issue is relevant only for miners, non-mining nodes are unaffected, since non-mining nodes use a smaller verification cache instead of a full DAG.",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/pull/21793",
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/",
+      "https://github.com/ethereum/go-ethereum/commit/567d41d9363706b4b13ce0903804e8acf214af49"
+    ],
+    "introduced": "v1.6.0",
+    "fixed": "v1.9.24",
+    "published": "2020-11-12",
+    "severity": "Medium",
+    "check": "Geth\\/v1\\.(6|7|8)\\..*|Geth\\/v1\\.9\\.2(1|2|3)-.*",
+    "CVE": "correct"
+  },
+  {
+    "name": "GoCrash",
+    "uid": "GETH-2020-02",
+    "summary": "A denial-of-service issue can be used to crash Geth nodes during block processing, due to an underlying bug in Go (CVE-2020-28362) versions < `1.15.5`, or `<1.14.12`",
+    "description": "The DoS issue can be used to crash all Geth nodes during block processing, the effects of which would be that a major part of the Ethereum network went offline.\n\nOutside of Go-Ethereum, the issue is most likely relevant for all forks of Geth (such as TurboGeth or ETC’s core-geth) which is built with versions of Go which contains the vulnerability.",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/",
+      "https://groups.google.com/g/golang-announce/c/NpBGTTmKzpM",
+      "https://github.com/golang/go/issues/42552"
+    ],
+    "fixed": "v1.9.24",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth.*\\/go1\\.(11(.*)|12(.*)|13(.*)|14|14\\.(\\d|10|11|)|15|15\\.[0-4])$"
+  },
+  {
+    "name": "ShallowCopy",
+    "uid": "GETH-2020-03",
+    "summary": "A consensus flaw in Geth, related to `datacopy` precompile",
+    "description": "Geth erroneously performed a 'shallow' copy when the precompiled `datacopy` (at `0x00...04`) was invoked. An attacker could deploy a contract that uses the shallow copy to corrupt the contents of the `RETURNDATA`, thus causing a consensus failure.",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/"
+    ],
+    "introduced": "v1.9.7",
+    "fixed": "v1.9.17",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth\\/v1\\.9\\.(7|8|9|10|11|12|13|14|15|16).*$"
+  },
+  {
+    "name": "GethCrash",
+    "uid": "GETH-2020-04",
+    "summary": "A denial-of-service issue can be used to crash Geth nodes during block processing",
+    "description": "Full details to be disclosed at a later date",
+    "links": [
+      "https://blog.ethereum.org/2020/11/12/geth_security_release/"
+    ],
+    "introduced": "v1.9.16",
+    "fixed": "v1.9.18",
+    "published": "2020-11-12",
+    "severity": "Critical",
+    "check": "Geth\\/v1\\.9.(16|17).*$"
+  }
+]
```

### cmd/geth/testdata/vcheck/minisig-sigs/vulnerabilities.json.minisig.1
```diff
@@ -0,0 +1,4 @@
+untrusted comment: signature from minisign secret key
+RWQkliYstQBOKFQFQTjmCd6TPw07VZyWFSB3v4+1BM1kv8eHLE5FDy2OkPEqtdaL53xftlrHoJQie0uCcovdlSV8kpyxiLrxEQ0=
+trusted comment: timestamp:1605618622	file:vulnerabilities.json
+osAPs4QPdDkmiWQxqeMIzYv/b+ZGxJ+19Sbrk1Cpq4t2gHBT+lqFtwL3OCzKWWyjGRTmHfsVGBYpzEdPRQ0/BQ==
```

### cmd/geth/testdata/vcheck/minisig-sigs/vulnerabilities.json.minisig.2
```diff
@@ -0,0 +1,4 @@
+untrusted comment: Here's a comment
+RWQkliYstQBOKFQFQTjmCd6TPw07VZyWFSB3v4+1BM1kv8eHLE5FDy2OkPEqtdaL53xftlrHoJQie0uCcovdlSV8kpyxiLrxEQ0=
+trusted comment: Here's a trusted comment
+3CnkIuz9MEDa7uNyGZAbKZhuirwfiqm7E1uQHrd2SiO4Y8+Akw9vs052AyKw0s5nhbYHCZE2IMQdHNjKwxEGAQ==
```

### cmd/geth/testdata/vcheck/minisig-sigs/vulnerabilities.json.minisig.3
```diff
@@ -0,0 +1,4 @@
+untrusted comment: One more (untrusted) comment
+RWQkliYstQBOKFQFQTjmCd6TPw07VZyWFSB3v4+1BM1kv8eHLE5FDy2OkPEqtdaL53xftlrHoJQie0uCcovdlSV8kpyxiLrxEQ0=
+trusted comment: Here's a trusted comment
+3CnkIuz9MEDa7uNyGZAbKZhuirwfiqm7E1uQHrd2SiO4Y8+Akw9vs052AyKw0s5nhbYHCZE2IMQdHNjKwxEGAQ==
```

### cmd/geth/testdata/vcheck/minisign.pub
```diff
@@ -0,0 +1,2 @@
+untrusted comment: minisign public key 284E00B52C269624
+RWQkliYstQBOKOdtClfgC3IypIPX6TAmoEi7beZ4gyR3wsaezvqOMWsp
```

### cmd/geth/testdata/vcheck/minisign.sec
```diff
@@ -0,0 +1,2 @@
+untrusted comment: minisign encrypted secret key
+RWRTY0Iyz8kmPMKrqk6DCtlO9a33akKiaOQG1aLolqDxs52qvPoAAAACAAAAAAAAAEAAAAAArEiggdvyn6+WzTprirLtgiYQoU+ihz/HyGgjhuF+Pz2ddMduyCO+xjCHeq+vgVVW039fbsI8hW6LRGJZLBKV5/jdxCXAVVQE7qTQ6xpEdO0z8Z731/pV1hlspQXG2PNd16NMtwd9dWw=
```

### cmd/geth/testdata/vcheck/signify-sigs/data.json.sig
```diff
@@ -0,0 +1,2 @@
+untrusted comment: verify with ./signifykey.pub
+RWSKLNhZb0KdAbhRUhW2LQZXdnwttu2SYhM9EuC4mMgOJB85h7/YIPupf8/ldTs4N8e9Y/fhgdY40q5LQpt5IFC62fq0v8U1/w8=
```

### cmd/geth/testdata/vcheck/signifykey.pub
```diff
@@ -0,0 +1,2 @@
+untrusted comment: signify public key
+RWSKLNhZb0KdATtRT7mZC/bybI3t3+Hv/O2i3ye04Dq9fnT9slpZ1a2/
```

### cmd/geth/testdata/vcheck/signifykey.sec
```diff
@@ -0,0 +1,2 @@
+untrusted comment: signify secret key
+RWRCSwAAACpLQDLawSQCtI7eAVIvaiHzjTsTyJsfV5aKLNhZb0KdAWeICXJGa93/bHAcsY6jUh9I8RdEcDWEoGxmaXZC+IdVBPxDpkix9fBRGEUdKWHi3dOfqME0YRzErWI5AVg3cRw=
```
