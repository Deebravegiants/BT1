# [H] GoBGP has Remote Denial of Service (Panic) in UpdatePathAttrs4ByteAs via Malformed BGP UPDATE

## Summary
Severity: High
Advisory: GHSA-8rxh-r2p6-7f2q
CVE: CVE-2026-41643
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-8rxh-r2p6-7f2q
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=0 <4.3.0

## Details
### Summary
A remote Denial of Service (DoS) vulnerability exists in GoBGP where a malformed BGP UPDATE message can trigger a runtime error: index out of range panic. This occurs during the processing of 4-byte AS attributes when the message structure causes an internal slice index shift that is not properly handled.

### Details
The vulnerability is located in internal/pkg/table/message.go within the UpdatePathAttrs4ByteAs function.

When GoBGP processes a BGP UPDATE message containing both an AS_PATH and an AS4_PATH attribute, it attempts to merge or validate them to support 4-byte AS numbers. If the attributes are ordered such that AS4_PATH (Type 17) appears before AS_PATH (Type 2), and the AS4_PATH is deemed invalid/malformed, the code attempts to remove the AS4_PATH attribute from the msg.PathAttributes slice.
It appears the crash happens due to an index shift in msg.PathAttributes:
```
#GoBGP v4.2.0
// Line 112: If AS4_PATH precedes AS_PATH, the deletion causes all subsequent attributes to shift left.
msg.PathAttributes = append(msg.PathAttributes[:as4AttrPos], msg.PathAttributes[as4AttrPos+1:]...)

// Line 206: The stale asAttrPos index is used here.
//The function continues to use the stale index (asAttrPos) to update the AS_PATH. Since the slice length has decreased, accessing the old index leads to a panic.
msg.PathAttributes[asAttrPos] = bgp.NewPathAttributeAsPath(newIntfParams)
```
This deletion causes all subsequent attributes in the slice to shift left by one position. However, the function continues to use the original asAttrPos index (calculated before the deletion) to access or modify the AS_PATH attribute later at [Line 206](https://www.google.com/search?q=https://github.com/osrg/gobgp/blob/v4.2.0/internal/pkg/table/message.go%23L206). Because the slice is now shorter, the "stale" index points out of bounds, triggering a panic and crashing the entire GoBGP process.
### PoC
Environment: * GoBGP version: 4.2.0
Configuration: Passive peering enabled.
Reproduction Steps:
Configure GoBGP with a neighbor (e.g., 192.168.31.195).
Send a specially crafted BGP UPDATE hex payload:
```
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
00 22 02
00 00                  # Withdrawn Routes Length
00 0b                  # Total Path Attribute Length
40 11 01 02            # AS4_PATH (Type 17, Len 1, Val 02) - Triggers the bug
40 02 04 ff ff de ad   # AS_PATH (Type 2, Len 4)
```
The GoBGP process will immediately crash with: panic: runtime error: index out of range [1] with length 1.

### Impact
Vulnerability Type: Remote Denial of Service (DoS).
Impacted Users: Any GoBGP deployment (v4.2.0 and earlier) that accepts BGP UPDATE messages from peers. Since this crash occurs in the FSM (Finite State Machine) handling loop, a single malicious peer or a malformed route propagated through a transit provider can consistently crash the BGP daemon, leading to a complete loss of routing capabilities.

## References
- https://github.com/osrg/gobgp/security/advisories/GHSA-8rxh-r2p6-7f2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41643
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/releases/tag/v4.3.0
