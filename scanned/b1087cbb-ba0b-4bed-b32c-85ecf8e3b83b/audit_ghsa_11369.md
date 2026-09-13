# [H] Sliver: Nil Pointer Dereference in tunnelCloseHandler causes panic when a reverse tunnel (rportfwd) close is attempted

## Summary
Severity: High
Advisory: GHSA-c279-989m-238f
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-c279-989m-238f
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=0

## Details
### Summary
A nil pointer dereference in `tunnelCloseHandler` causes the handler goroutine to panic whenever a reverse tunnel (rportfwd) close is attempted. Both the legitimate close path AND the unauthorized close path dereference `tunnel.SessionID` where `tunnel` is guaranteed nil. This means rportfwd tunnels can never be cleanly closed, and any authenticated implant can trigger repeated goroutine panics.

### Details
File: `server/handlers/sessions.go` lines 172 and 175

The function enters an `else` block precisely because `core.Tunnels.Get(tunnelData.TunnelID)` returned `nil`. Both conditions inside that else block then dereference `tunnel.SessionID` instead of `rtunnel.SessionID`:
```go
} else {
    rtunnel := rtunnels.GetRTunnel(tunnelData.TunnelID)

    if rtunnel != nil && session.ID == tunnel.SessionID {      // LINE 172 — nil deref
        rtunnel.Close()
        rtunnels.RemoveRTunnel(rtunnel.ID)
    } else if rtunnel != nil && session.ID != tunnel.SessionID { // LINE 175 — nil deref
        sessionHandlerLog.Warnf("...")
    }
}
```

Note: The identical bug was already fixed in `tunnelDataHandler` at lines 124/126 (correctly uses `rtunnel.SessionID`), but the fix was 
not applied to `tunnelCloseHandler`.

### PoC
```go
tunnel := GetTunnel(999)   // returns nil — no normal tunnel with this ID
// tunnel is nil here

rtunnel := GetRTunnel(999) // returns valid rtunnel owned by session-AAAA

// Both lines below panic with:
// runtime error: invalid memory address or nil pointer dereference
if rtunnel != nil && sessionID == tunnel.SessionID { ... }      // line 172
} else if rtunnel != nil && sessionID != tunnel.SessionID { ... } // line 175
```

Confirmed on master commit `7ac4db3fa` with standalone reproducer.
Output:
```
PANIC on line 172 (legitimate close): runtime error: invalid memory address or nil pointer dereference
PANIC on line 175 (unauthorized close): runtime error: invalid memory address or nil pointer dereference
```

![1](https://github.com/user-attachments/assets/93b24286-3282-454f-80a4-b01abe4f1d63)
![2](https://github.com/user-attachments/assets/d4219aea-eb18-474c-b69a-a5e20e97161f)
![3](https://github.com/user-attachments/assets/5a76b0d7-ae5b-4d91-bfe9-730d3e5c322c)

### Impact
- rportfwd tunnels **cannot be closed** — functional regression
- Any authenticated implant can trigger repeated handler goroutine panics
- rtunnel map entries leak (never cleaned up on close failure)
- `recoverAndLogPanic()` prevents full server crash but silently drops the close operation

### Fix
Replace `tunnel.SessionID` with `rtunnel.SessionID` on both lines:
```diff
-  if rtunnel != nil && session.ID == tunnel.SessionID {
+  if rtunnel != nil && session.ID == rtunnel.SessionID {
       rtunnel.Close()
       rtunnels.RemoveRTunnel(rtunnel.ID)
-  } else if rtunnel != nil && session.ID != tunnel.SessionID {
+  } else if rtunnel != nil && session.ID != rtunnel.SessionID {
```

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-c279-989m-238f
- https://github.com/BishopFox/sliver
