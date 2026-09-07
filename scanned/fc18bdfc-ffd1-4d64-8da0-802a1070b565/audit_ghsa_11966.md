# [H] OpenClaw Canvas Authentication Bypass Vulnerability

## Summary
Severity: High
Advisory: GHSA-vvjh-f6p9-5vcf
CWE: CWE-291
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-vvjh-f6p9-5vcf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
ZDI-CAN-29311: OpenClaw Canvas Authentication Bypass Vulnerability

-- ABSTRACT -------------------------------------

Trend Micro's Zero Day Initiative has identified a vulnerability affecting the following products:
OpenClaw - OpenClaw

-- VULNERABILITY DETAILS ------------------------
* Version tested: openclaw 2026.2.17
* Platform tested: macOS 26.3

---

### Analysis

## Description

The OpenClaw gateway's `authorizeCanvasRequest()` function implements an IP-based authentication fallback for canvas endpoints (`/__openclaw__/a2ui/`, `/__openclaw__/canvas/`, `/__openclaw__/ws`). When a WebSocket client authenticates from a private IP address, ALL subsequent HTTP requests from that same IP are granted canvas access without requiring their own authentication token.

In environments where multiple clients share a single IP address ��� corporate NAT, VPN concentrators, Kubernetes clusters, Docker host-mode networking ��� an unauthenticated attacker on the same network is granted full canvas access by virtue of sharing an IP with a legitimate authenticated client.

## Root Cause

Three functions in `src/gateway/server-http.ts` create this vulnerability:

### 1. IP-matching function (line ~100)

```typescript
function hasAuthorizedWsClientForIp(clients: Set<GatewayWsClient>, clientIp: string): boolean {
  for (const client of clients) {
    if (client.clientIp && client.clientIp === clientIp) {
      return true;
    }
  }
  return false;
}
```

This function checks if ANY connected WebSocket client shares the same IP. It does not verify that the HTTP request belongs to the same user, session, or browser as the WS client.

### 2. IP-based fallback in authorizeCanvasRequest (line ~109)

```typescript
async function authorizeCanvasRequest(params: { ... }): Promise<GatewayAuthResult> {
  // ... token check first ...

  const clientIp = resolveGatewayClientIp({ ... });

  // Only allow fallback for private/loopback addresses
  if (!isPrivateOrLoopbackAddress(clientIp)) {
    return lastAuthFailure ?? { ok: false, reason: "unauthorized" };
  }

  // THE VULNERABILITY: grants access based on IP alone
  if (hasAuthorizedWsClientForIp(clients, clientIp)) {
    return { ok: true };
  }

  return lastAuthFailure ?? { ok: false, reason: "unauthorized" };
}
```

If the HTTP request comes from a private IP that matches any authenticated WS client, access is granted without verifying the request's own credentials.

### 3. Canvas path routing

```typescript
function isCanvasPath(pathname: string): boolean {
  return (
    pathname === A2UI_PATH ||              // /__openclaw__/a2ui
    pathname.startsWith(`${A2UI_PATH}/`) ||
    pathname === CANVAS_HOST_PATH ||        // /__openclaw__/canvas
    pathname.startsWith(`${CANVAS_HOST_PATH}/`) ||
    pathname === CANVAS_WS_PATH            // /__openclaw__/ws
  );
}
```

All canvas endpoints use this weaker authentication path instead of the standard `authorizeGatewayConnect()` which requires a valid token.

## Attack Scenario

### Corporate NAT Environment

1. A company runs an OpenClaw gateway on an internal server with `--bind lan` and a token for authentication.
2. Developer Alice connects her OpenClaw desktop app via WebSocket using her valid token. The gateway records her IP as the corporate NAT address (e.g., `10.0.0.1`).
3. Attacker Bob, on the same corporate network, also appears as `10.0.0.1` to the gateway (NAT).
4. Bob sends an HTTP request to `http://gateway:18789/__openclaw__/a2ui/` with NO authentication header.
5. `authorizeCanvasRequest()` checks: Is `10.0.0.1` a private IP? Yes. Is there a WS client from `10.0.0.1`? Yes (Alice). Access granted.
6. Bob now has full access to all canvas endpoints ��� the A2UI interface, canvas content, and the canvas WebSocket ��� without ever authenticating.

### Kubernetes / Docker Environments

In containerized deployments using shared networking (host mode, pod networking), multiple containers share the same IP. One container's authentication enables canvas access for all containers on that IP.

## Reproduction Steps

### Prerequisites
- Docker installed
- Python 3
- OpenClaw Docker image built as `openclaw:local`

### Steps

1. Navigate to the PoC directory and start the environment:
   ```bash
   cd vulnerabilities/04-canvas-ip-auth-bypass
   docker compose up -d --wait
   ```

2. This starts two containers on a shared Docker network:
   - **Gateway** (172.28.0.10): Token-protected OpenClaw gateway
   - **Legitimate client** (172.28.0.20): Connects via WebSocket with valid token, establishing IP trust

3. Wait a few seconds for the legitimate client to authenticate, then run the PoC:
   ```bash
   python3 poc.py
   ```

4. The PoC runs three tests:

   | Test | Source | Source IP | Token | Result |
   |------|--------|-----------|-------|--------|
   | 1 ��� Host (different IP) | Host machine | Host bridge IP | None | **401 Unauthorized** |
   | 2 ��� Host with token (control) | Host machine | Host bridge IP | Valid | **200 OK** |
   | 3 ��� **Same IP (exploit)** | **docker exec into legit container** | **172.28.0.20** | **None** | **200 OK** |

5. Test 3 is the exploit: `poc.py` uses `docker exec` to run an HTTP request from inside the legitimate client's container (IP 172.28.0.20) with **no** `Authorization` header. The gateway's `authorizeCanvasRequest()` matches the source IP against the authenticated WebSocket client and returns `200 OK` ��� granting full canvas access without credentials.

6. Cleanup:
   ```bash
   docker compose down -v
   ```

## Impact

- **Authentication Bypass**: Any unauthenticated client sharing an IP with a legitimate WS-authenticated client gains full canvas endpoint access.
- **Information Disclosure**: Canvas endpoints serve:
  - The A2UI (Agent-to-User Interface) rendered content, which may contain sensitive data the AI agent is presenting to the user
  - The canvas HTML/JS application
  - The canvas WebSocket upgrade endpoint
- **Scope**: Affects all deployments where the gateway is network-exposed (`--bind lan`) and clients share IP addresses (NAT, VPN, K8s, corporate networks).
- **No auth required**: The attacker needs only network adjacency; no credentials, tokens, or user interaction.



-- CREDIT ---------------------------------------
This vulnerability was discovered by:
Peter Girnus (@gothburz) and Project AESIR of TrendAI Zero Day Initiative

-- FURTHER DETAILS ------------------------------

Supporting files: 
[ZDI-CAN-29311.zip](https://github.com/user-attachments/files/25445235/ZDI-CAN-29311.zip)


If supporting files were contained with this report they are provided within a password protected ZIP file. The password is the ZDI candidate number in the form: ZDI-CAN-XXXX where XXXX is the ID number.

Zero Day Initiative
zdi-disclosures@trendmicro.com

The PGP key used for all ZDI vendor communications is available from:

  http://www.zerodayinitiative.com/documents/disclosures-pgp-key.asc

-- INFORMATION ABOUT THE ZDI --------------------
Established by TippingPoint and acquired by Trend Micro, the Zero Day Initiative (ZDI) neither re-sells vulnerability details nor exploit code. Instead, upon notifying the affected product vendor, the ZDI provides its Trend Micro TippingPoint customers with zero day protection through its intrusion prevention technology. Explicit details regarding the specifics of the vulnerability are not exposed to any parties until an official vendor patch is publicly available.

Please contactZero Day Initiative for further details or refer to:

  http://www.zerodayinitiative.com

-- DISCLOSURE POLICY ----------------------------

Zero Day Initiative's vulnerability disclosure policy is available online at:

  http://www.zerodayinitiative.com/advisories/disclosure_policy/
    

## Fix Commit(s)
- `c45f3c5b004c8d63dc0e282e2176f8c9355d24f1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vvjh-f6p9-5vcf
- https://github.com/openclaw/openclaw/commit/c45f3c5b004c8d63dc0e282e2176f8c9355d24f1
- https://github.com/openclaw/openclaw
