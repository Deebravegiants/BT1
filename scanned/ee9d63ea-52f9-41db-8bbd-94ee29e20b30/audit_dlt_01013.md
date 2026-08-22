# [M] go-f3 Vulnerable to Cached Justification Verification Bypass

## Summary
Severity: Medium
Chain: github.com/filecoin-project/go-f3
Component: github.com/filecoin-project/go-f3
CVE: CVE-2025-59941
CWE: Authentication Bypass by Primary Weakness
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-7pq9-rf9p-wcrf
Type: github-advisory

## Details
### Description
A vulnerability exists in go-f3's justification verification caching mechanism where verification results are cached without properly considering the context of the message. An attacker can bypass justification verification by:
1. First submitting a valid message with a correct justification
2. Then reusing the same cached justification in contexts where it would normally be invalid

This occurs because the cached verification does not properly validate the relationship between the justification and the specific message context it's being used with.

### Impact
- Potential consensus integrity issues through invalid justification acceptance
- Could affect network liveness if exploited systematically
- May allow malicious actors to influence consensus decisions with invalid justifications
- Requires significant power (350+ TiB due to power table rounding) to meaningfully exploit
- It would also be difficult to exploit in a synchronised fashion, such that >1/3 of the network goes down at one time.  This isn't a one-msg panic, where you can spam it and bring everyone down, because every node will have a different amount of memory andmany SPs also run redundant lotus nodes.  

### Patches
The fix was merged and released with go-f3 0.8.9. All node software (Lotus, Forest, Venus) are using a patched version of go-f3 with their updates for the nv27 network upgrade.

### Workarounds
The are no immediate workarounds available. Nodes should upgrade to the patched version, which they will have done if participating in nv27 on Filecoin mainnet.

### Credits
The bug was reported by @lgprbs via our bug bounty program. Thank you for the contributions.
