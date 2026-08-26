# [C] CVE-2026-34202: Remote Denial of Service via Crafted V5 Transactions

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-34202
CWE: Uncaught Exception
Published: 2026-03-27
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qp6f-w4r3-h8wg
Type: github-advisory

## Details
---

# CVE-2026-34202: Remote Denial of Service via Crafted V5 Transactions

## Summary
A vulnerability in Zebra's transaction processing logic allows a remote, unauthenticated attacker to cause a Zebra node to panic (crash). This is triggered by sending a specially crafted V5 transaction that passes initial deserialization but fails during transaction ID calculation.

## Severity
**Critical** - This is a Remote Denial of Service (DoS) that requires no authentication and can be triggered by a single network message.

## Affected Versions
All Zebra versions supporting V5 transactions (Network Upgrade 5 and later) prior to **version 4.3.0**.

## Description
The vulnerability stems from Zebra lazily validating transaction fields that are eagerly validated in the librustzcash parsing logic used when Zebra computes transaction ids and auth digests for V5 transactions where Zebra panics if those computations fail.

`PushTransaction` messages with malformed V5 transactions are successfully deserialized as the zebra-chain `Transaction` type by the network codec, but when Zebra converts those transactions into internal types to compute the TxID expecting it to succeed, it triggers a panic/crash.

An attacker can trigger this crash by sending a single crafted `tx` message to a Zebra node's public P2P port. The same issue can be triggered via the `sendrawtransaction` RPC method.

## Impact
**Remote Denial of Service**
* **Attack Vector:** Remote, unauthenticated.
* **Effect:** Immediate crash of the Zebra node.
* **Scope:** Any node with an open P2P port (default 8233) or exposed RPC interface is vulnerable.

## Fixed Versions
This issue is fixed in **Zebra 4.3.0**. 

The fix ensures that any transaction that would fail TxID calculation is rejected during the initial deserialization phase, and replaces internal panics with graceful error handling.

## Mitigation
Users should upgrade to **Zebra 4.3.0** or later immediately. 

If an immediate upgrade is not possible, users should ensure their RPC port is not exposed to the Internet. However, the P2P port must remain closed or restricted to trusted peers to fully mitigate the risk, which may impact the node's ability to sync with the network.

## References
* [Zebra 4.3.0 Release Announcement](https://zfnd.org/zebra-4-3-0-critical-security-fixes-zip-235-support-and-performance-improvements/)

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qp6f-w4r3-h8wg_
