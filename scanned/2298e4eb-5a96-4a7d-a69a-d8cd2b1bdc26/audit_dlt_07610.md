# [?] cmd/geth: update vulnerabilities.json testdata (#24856)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-05-16
Source: https://github.com/ethereum/go-ethereum/commit/af806168b62b6a0e772b73ce25d31d8e61d26043
Type: security-commit

## Details
cmd/geth: update vulnerabilities.json testdata (#24856)

## Patch
### cmd/geth/testdata/vcheck/vulnerabilities.json
```diff
@@ -112,8 +112,59 @@
     ],
     "introduced": "v1.10.1",
     "fixed": "v1.10.6",
-    "published": "2020-12-10",
+    "published": "2021-07-22",
     "severity": "High",
     "check": "(Geth\\/v1\\.10\\.(1|2|3|4|5)-.*)$"
+  },
+  {
+    "name": "RETURNDATA corruption via datacopy",
+    "uid": "GETH-2021-02",
+    "summary": "A consensus-flaw in the Geth EVM could cause a node to deviate from the canonical chain.",
+    "description": "A memory-corruption bug within the EVM can cause a consensus error, where vulnerable nodes obtain a different `stateRoot` when processing a maliciously crafted transaction. This, in turn, would lead to the chain being split: mainnet splitting in two forks.\n\nAll Geth versions supporting the London hard fork are vulnerable (the bug is older than London), so all users should update.\n\nThis bug was exploited on Mainnet at block 13107518.\n\nCredits for the discovery go to @guidovranken (working for Sentnl during an audit of the Telos EVM) and reported via bounty@ethereum.org.",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/blob/master/docs/postmortems/2021-08-22-split-postmortem.md",
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-9856-9gg9-qcmq",
+      "https://github.com/ethereum/go-ethereum/releases/tag/v1.10.8"
+    ],
+    "introduced": "v1.10.0",
+    "fixed": "v1.10.8",
+    "published": "2021-08-24",
+    "severity": "High",
+    "CVE": "CVE-2021-39137",
+    "check": "(Geth\\/v1\\.10\\.(0|1|2|3|4|5|6|7)-.*)$"
+  },
+  {
+    "name": "DoS via malicious `snap/1` request",
+    "uid": "GETH-2021-03",
+    "summary": "A vulnerable node is susceptible to crash when processing a maliciously crafted message from a peer, via the snap/1 protocol. The crash can be triggered by sending a malicious snap/1 GetTrieNodes package.",
+    "description": "The `snap/1` protocol handler contains two vulnerabilities related to the `GetTrieNodes` packet, which can be exploited to crash the node. Full details are available at the Github security [advisory](https://github.com/ethereum/go-ethereum/security/advisories/GHSA-59hh-656j-3p7v)",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-59hh-656j-3p7v",
+      "https://geth.ethereum.org/docs/vulnerabilities/vulnerabilities",
+      "https://github.com/ethereum/go-ethereum/pull/23657"
+    ],
+    "introduced": "v1.10.0",
+    "fixed": "v1.10.9",
+    "published": "2021-10-24",
+    "severity": "Medium",
+    "CVE": "CVE-2021-41173",
+    "check": "(Geth\\/v1\\.10\\.(0|1|2|3|4|5|6|7|8)-.*)$"
+  },
+  {
+    "name": "DoS via malicious p2p message",
+    "uid": "GETH-2022-01",
+    "summary": "A vulnerable node can crash via p2p messages sent from an attacker node, if running with non-default log options.",
+    "description": "A vulnerable node, if configured to use high verbosity logging, can be made to crash when handling specially crafted p2p messages sent from an attacker node. Full details are available at the Github security [advisory](https://github.com/ethereum/go-ethereum/security/advisories/GHSA-wjxw-gh3m-7pm5)",
+    "links": [
+      "https://github.com/ethereum/go-ethereum/security/advisories/GHSA-wjxw-gh3m-7pm5",
+      "https://geth.ethereum.org/docs/vulnerabilities/vulnerabilities",
+      "https://github.com/ethereum/go-ethereum/pull/24507"
+    ],
+    "introduced": "v1.10.0",
+    "fixed": "v1.10.17",
+    "published": "2022-05-11",
+    "severity": "Low",
+    "CVE": "CVE-2022-29177",
+    "check": "(Geth\\/v1\\.10\\.(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16)-.*)$"
   }
 ]
```
