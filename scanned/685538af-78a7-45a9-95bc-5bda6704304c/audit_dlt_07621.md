# [?] cmd/geth: update vulnerability testdata (#23252)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-07-27
Source: https://github.com/ethereum/go-ethereum/commit/5c89ec9b989084dfc67dcaf81736067ebb8f078c
Type: security-commit

## Details
cmd/geth: update vulnerability testdata (#23252)

## Patch
### cmd/geth/testdata/vcheck/vulnerabilities.json
```diff
@@ -52,19 +52,68 @@
     "check": "Geth\\/v1\\.9\\.(7|8|9|10|11|12|13|14|15|16).*$"
   },
   {
-    "name": "GethCrash",
+    "name": "Geth DoS via MULMOD",
     "uid": "GETH-2020-04",
     "summary": "A denial-of-service issue can be used to crash Geth nodes during block processing",
-    "description": "Full details to be disclosed at a later date",
+    "description": "Affected versions suffer from a vulnerability which can be exploited through the `MULMOD` operation, by specifying a modulo of `0`: `mulmod(a,b,0)`, causing a `panic` in the underlying library. \nThe crash was in the `uint256` library, where a buffer [underflowed](https://github.com/holiman/uint256/blob/4ce82e695c10ddad57215bdbeafb68b8c5df2c30/uint256.go#L442).\n\n\tif `d == 0`, `dLen` remains `0`\n\nand https://github.com/holiman/uint256/blob/4ce82e695c10ddad57215bdbeafb68b8c5df2c30/uint256.go#L451 will try to access index `[-1]`.\n\nThe `uint256` library was first merged in this [commit](https://github.com/ethereum/go-ethereum/commit/cf6674539c589f80031f3371a71c6a80addbe454), on 2020-06-08. \nExploiting this vulnerabilty would cause all vulnerable nodes to drop off the network. \n\nThe issue was brought to our attention through a [bug report](https://github.com/ethereum/go-ethereum/issues/21367), showing a `panic` occurring on sync from genesis on the Ropsten network.\n \nIt was estimated that the least obvious way to fix this would be to merge the fix into `uint256`, make a new release of that library and then update the geth-dependency.\n",
     "links": [
       "https://blog.ethereum.org/2020/11/12/geth_security_release/",
-      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-jm5c-rv3w-w83m"
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-jm5c-rv3w-w83m",
+      "https://github.com/holiman/uint256/releases/tag/v1.1.1",
+      "https://github.com/holiman/uint256/pull/80",
+      "https://github.com/ethereum/go-ethereum/pull/21368"
     ],
     "introduced": "v1.9.16",
     "fixed": "v1.9.18",
     "published": "2020-11-12",
     "severity": "Critical",
     "CVE": "CVE-2020-26242",
     "check": "Geth\\/v1\\.9.(16|17).*$"
+  },
+  {
+    "name": "LES Server DoS via GetProofsV2",
+    "uid": "GETH-2020-05",
+    "summary": "A DoS vulnerability can make a LES server crash.",
+    "description": "A DoS vulnerability can make a LES server crash via malicious GetProofsV2 request from a connected LES client.\n\nThe vulnerability was patched in #21896.\n\nThis vulnerability only concern users explicitly running geth as a light server",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-r33q-22hv-j29q",
+      "https://github.com/ethereum/go-ethereum/pull/21896"
+    ],
+    "introduced": "v1.8.0",
+    "fixed": "v1.9.25",
+    "published": "2020-12-10",
+    "severity": "Medium",
+    "CVE": "CVE-2020-26264",
+    "check": "(Geth\\/v1\\.8\\.*)|(Geth\\/v1\\.9\\.\\d-.*)|(Geth\\/v1\\.9\\.1\\d-.*)|(Geth\\/v1\\.9\\.(20|21|22|23|24)-.*)$"
+  },
+  {
+    "name": "SELFDESTRUCT-recreate consensus flaw",
+    "uid": "GETH-2020-06",
+    "introduced": "v1.9.4",
+    "fixed": "v1.9.20",
+    "summary": "A consensus-vulnerability in Geth could cause a chain split, where vulnerable versions refuse to accept the canonical chain.",
+    "description": "A flaw was repoted at 2020-08-11 by John Youngseok Yang (Software Platform Lab), where a particular sequence of transactions could cause a consensus failure.\n\n- Tx 1:\n - `sender` invokes `caller`.\n - `caller` invokes `0xaa`. `0xaa` has 3 wei, does a self-destruct-to-self\n - `caller` does a  `1 wei` -call to `0xaa`, who thereby has 1 wei (the code in `0xaa` still executed, since the tx is still ongoing, but doesn't redo the selfdestruct, it takes a different path if callvalue is non-zero)\n\n-Tx 2:\n - `sender` does a 5-wei call to 0xaa. No exec (since no code). \n\nIn geth, the result would be that `0xaa` had `6 wei`, whereas OE reported (correctly) `5` wei. Furthermore, in geth, if the second tx was not executed, the `0xaa` would be destructed, resulting in `0 wei`. Thus obviously wrong. \n\nIt was determined that the root cause was this [commit](https://github.com/ethereum/go-ethereum/commit/223b950944f494a5b4e0957fd9f92c48b09037ad) from [this PR](https://github.com/ethereum/go-ethereum/pull/19953). The semantics of `createObject` was subtly changd, into returning a non-nil object (with `deleted=true`) where it previously did not if the account had been destructed. This return value caused the new object to inherit the old `balance`.\n",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-xw37-57qp-9mm4"
+    ],
+    "published": "2020-12-10",
+    "severity": "High",
+    "CVE": "CVE-2020-26265",
+    "check": "(Geth\\/v1\\.9\\.(4|5|6|7|8|9)-.*)|(Geth\\/v1\\.9\\.1\\d-.*)$"
+  },
+  {
+    "name": "Not ready for London upgrade",
+    "uid": "GETH-2021-01",
+    "summary": "The client is not ready for the 'London' technical upgrade, and will deviate from the canonical chain when the London upgrade occurs (at block '12965000' around August 4, 2021.",
+    "description": "At (or around) August 4, Ethereum will undergo a technical upgrade called 'London'. Clients not upgraded will fail to progress on the canonical chain.",
+    "links": [
+      "https://github.com/ethereum/eth1.0-specs/blob/master/network-upgrades/mainnet-upgrades/london.md",
+      "https://notes.ethereum.org/@timbeiko/ropsten-postmortem"
+    ],
+    "introduced": "v1.10.1",
+    "fixed": "v1.10.6",
+    "published": "2020-12-10",
+    "severity": "High",
+    "check": "(Geth\\/v1\\.10\\.(1|2|3|4|5)-.*)$"
   }
 ]
```
