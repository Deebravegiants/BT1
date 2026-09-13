# [H] free5GC AUSF authentication contexts can be overwritten by concurrent requests for the same SUPI

## Summary
Severity: High
Advisory: GHSA-334q-h5g3-fpxv
CVE: CVE-2026-55784
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-334q-h5g3-fpxv
Type: github-advisory

## Affected
- Go: `github.com/free5gc/ausf` — affected >=0

## Details
### Summary

The AUSF component of free5GC stores per-subscriber authentication state in a global `sync.Map` keyed only by SUPI. Every incoming authentication request creates a new `AusfUeContext` and stores it under that SUPI key without checking whether an authentication procedure is already in progress and without generating a per-session unique identifier.

An attacker with access to the AUSF SBI/N12 interface can send concurrent `POST /nausf-auth/v1/ue-authentications` requests for the same target SUPI. Each request is accepted and overwrites the previous authentication context. A valid EAP-AKA' response for an earlier challenge is then verified against the latest overwritten context, whose `K_aut`, `XRES`, and `EapID` no longer match the challenge. The result is a targeted authentication denial of service for that SUPI while the request flood is maintained.

This issue was confirmed on `github.com/free5gc/ausf` v1.4.4 and current main as of June 2026.

### Details

The vulnerable context pool is defined in `internal/context/context.go`.

`UePool` is a `sync.Map`, which makes individual map operations safe, but it does not make the authentication procedure state safe. The problem is the session design: the key is only the SUPI, and `Store()` unconditionally replaces any active context for that SUPI.

```go
type AUSFContext struct {
    suciSupiMap sync.Map
    UePool      sync.Map
    // ...
}

type AusfUeContext struct {
    Supi string
    // ...

    // for EAP-AKA'
    K_aut    string
    XRES     string
    Rand     string
    EapID    uint8
    Resynced bool
}

func NewAusfUeContext(identifier string) (ausfUeContext *AusfUeContext) {
    ausfUeContext = new(AusfUeContext)
    ausfUeContext.Supi = identifier
    return ausfUeContext
}

func AddAusfUeContextToPool(ausfUeContext *AusfUeContext) {
    ausfContext.UePool.Store(ausfUeContext.Supi, ausfUeContext)
}
```

The vulnerable sequence is executed for every authentication request in `internal/sbi/processor/ue_authentication.go`:

```go
ueid := authInfoResult.Supi
ausfUeContext := ausf_context.NewAusfUeContext(ueid)
ausfUeContext.ServingNetworkName = snName
ausfUeContext.AuthStatus = models.AusfUeAuthenticationAuthResult_ONGOING
ausfUeContext.UdmUeauUrl = udmUrl
ausf_context.AddAusfUeContextToPool(ausfUeContext)
```

There is no guard such as `LoadOrStore`, no `AUTHENTICATION_IN_PROGRESS` response, no rate limit per SUPI, and no unique authentication-session ID in the context URL. For EAP-AKA', the returned context URL is derived directly from the SUCI/SUPI path:

```text
/nausf-auth/v1/ue-authentications/{suci}/eap-session
```

All concurrent authentication attempts for the same subscriber therefore point to the same logical context URL, while the backing `AusfUeContext` in `UePool` is repeatedly replaced.

When the EAP response is later processed, the AUSF looks up the current context by SUPI:

```go
currentSupi := ausf_context.GetSupiFromSuciSupiMap(eapSessionID)
ausfCurrentContext := ausf_context.GetAusfUeContext(currentSupi)
```

The EAP-AKA' response is then verified against the current context's `K_aut` and `XRES`:

```go
K_autStr := ausfCurrentContext.K_aut
XMAC := CalculateAtMAC(K_aut, decodeEapAkaPrimePkt.MACInput)
MAC := decodeEapAkaPrimePkt.Attributes[ausf_context.AT_MAC_ATTRIBUTE].Value
XRES := ausfCurrentContext.XRES
RES := hex.EncodeToString(decodeEapAkaPrimePkt.Attributes[ausf_context.AT_RES_ATTRIBUTE].Value)

if !bytes.Equal(MAC, XMAC) {
    eapOK = false
    eapErrStr = "EAP-AKA' integrity check fail"
} else if XRES == RES {
    logger.AuthELog.Infoln("Correct RES value, EAP-AKA' auth succeed")
    // ...
}
```

If another request has overwritten the context between challenge issuance and response processing, the legitimate response is checked against the wrong `K_aut` and fails the AT_MAC verification.

### Attack flow

The attack is selective for a target SUPI:

1. The legitimate procedure starts and the AUSF stores `ctx_LEGIT` under `UePool[target_supi]`.
2. The attacker sends many concurrent authentication requests for the same target SUCI/SUPI.
3. Each request obtains a new authentication vector and stores a new context under the same SUPI key.
4. `ctx_LEGIT` is overwritten by `ctx_ATTACK`.
5. The legitimate EAP response, computed with `K_aut_LEGIT`, reaches `/eap-session`.
6. The AUSF retrieves `ctx_ATTACK` by SUPI and computes `XMAC` with `K_aut_ATTACK`.
7. AT_MAC verification fails and the AUSF returns an EAP-AKA' notification failure.


When later contexts carry different session material, a continuous flood prevents the target subscriber from completing authentication because the AUSF's stored context keeps changing before the response is processed.

### PoC and evidence

The issue was reproduced in two phases in a controlled free5GC lab.

#### Phase 1: context overwrite

Experiment:

- 3 rounds of 8 concurrent `POST /nausf-auth/v1/ue-authentications` requests.
- Same target SUCI: `suci-0-001-01-0-0-0-0000000002`.
- AUSF listening on `0.0.0.0:8100`; PoC connected to `127.0.0.1:8100`.

Observed result:

- 24/24 requests returned HTTP 201.
- 24 distinct EapIDs were issued:

```text
[131, 11, 157, 99, 182, 232, 127, 228, 119, 36, 104, 10,
 107, 61, 66, 26, 110, 9, 210, 202, 53, 224, 237, 86]
```

- All responses used the same auth context URL:

```text
/nausf-auth/v1/ue-authentications/suci-0-001-01-0-0-0-0000000002/eap-session
```

- AUSF logs showed repeated context creation for the same SUCI/SUPI in a short interval:

```text
Add SuciSupiPair (suci-0-001-01-0-0-0-0000000002, imsi-001010000000002) to map.
Use EAP-AKA' auth method
| 201 | POST | /nausf-auth/v1/ue-authentications
...
```

This confirms that concurrent authentication requests for the same SUPI are accepted independently but collapse onto one shared context key.

#### Phase 2: valid EAP response fails after overwrite

The second PoC used a mock UDM with h2c support that returns different EAP-AKA' vectors by request counter for the same SUCI. This makes the overwrite directly observable:

| Request | Vector class | XRES | Effect |
|---|---|---|---|
| 1st | LEGIT | `0102030405060708` | response client computes AT_MAC with `K_aut_LEGIT` |
| 2nd and later | ATTACK | `deadbeefcafe0000` | flood overwrites AUSF context with `K_aut_ATTACK` |

Baseline without flood:

```text
POST /ue-authentications
  -> EapID=120, context with K_aut_LEGIT stored

POST /eap-session with AT_MAC(K_aut_LEGIT)
  -> AUSF log: Correct RES value, EAP-AKA' auth succeed
  -> HTTP 200, EAP success
```

Race condition run:

```text
POST /ue-authentications
  -> EapID=243, context with K_aut_LEGIT stored

20 concurrent POST /ue-authentications requests for the same SUCI
  -> 20/20 accepted
  -> K_aut_ATTACK overwrites K_aut_LEGIT in UePool

POST /eap-session with AT_MAC(K_aut_LEGIT)
  -> AUSF validates against K_aut_ATTACK
  -> AUSF log: EAP-AKA' failure: EAP-AKA' integrity check fail
  -> HTTP 200, EAP notification failure
```

Critical AUSF log excerpt:

```text
Add SuciSupiPair (suci-0-001-01-0-0-0-0000000002, imsi-001010000000002) to map.
... repeated for the same SUCI/SUPI ...
EapAuthComfirmRequest
[WARN] EAP-AKA' failure: EAP-AKA' integrity check fail
| 200 | 127.0.0.1 | POST | /nausf-auth/v1/ue-authentications/.../eap-session |
```

Baseline and attack logs are in the private evidence bundle:

```text
hallazgos/finding13-ausf-auth-race/evidencia/20260527-195933-race-condition-p2-final/
```

The final PoC uses a Python client that constructs a protocol-valid synthetic EAP-AKA' response from known vectors. It is not a full UERANSIM/AMF trace, and the P2 run uses a mock UDM returning distinct LEGIT/ATTACK vectors to make the overwrite observable. The synthetic response is sufficient to prove the AUSF state bug because the baseline succeeds with the same client and vectors, while the flood run fails at the exact AT_MAC check predicted by the code.

### Impact

The confirmed impact is targeted denial of authentication service for a chosen SUPI.

An attacker with access to the AUSF SBI/N12 interface can keep a subscriber from authenticating by continuously overwriting that subscriber's AUSF context. The AUSF process remains running; this is not a process crash and does not expose authentication material to the attacker. The availability impact is on the AUSF's primary security function for the targeted subscriber.

In the default free5GC deployment observed in the lab, the AUSF reported OAuth2 disabled and listened on `0.0.0.0:8100`. In a production deployment with strict SBI isolation, mTLS, OAuth2, or firewalling, the attacker would need access to the internal SBA network or control of a network function that can send AUSF authentication requests.

### Suggested remediation

The most robust fix is to stop using SUPI as the sole authentication-session key.

Recommended design:

1. Generate a unique session identifier for every authentication request.
2. Store the `AusfUeContext` under that session identifier.
3. Return the session identifier in the auth context URL.
4. On `/eap-session` or `/5g-aka-confirmation`, retrieve the exact session context by session ID rather than by SUPI.

Conceptual example:

```go
sessionID := uuid.New().String()
ausfUeContext := ausf_context.NewAusfUeContext(sessionID)
ausfUeContext.Supi = ueid
// populate context...
ausf_context.AddAusfUeContextToPool(ausfUeContext)

// Return:
// /nausf-auth/v1/ue-authentications/{sessionID}/eap-session
```

If the intended behavior is to allow only one active authentication procedure per SUPI, use an atomic check-and-insert operation and reject concurrent attempts explicitly:

```go
if existing, loaded := ausf_context.LoadOrStoreAusfUeContext(ueid, newCtx); loaded {
    if existing.AuthStatus == models.AusfUeAuthenticationAuthResult_ONGOING {
        c.JSON(http.StatusConflict, models.ProblemDetails{
            Status: http.StatusConflict,
            Cause:  "AUTHENTICATION_IN_PROGRESS",
        })
        return
    }
}
```

A mutex inside `AusfUeContext` alone is not sufficient if new requests are still allowed to replace the global map entry for the same SUPI.

Additional hardening:

- Apply per-SUPI rate limiting on `POST /ue-authentications`.
- Enable and enforce OAuth2/mTLS for SBI access in deployments.
- Add tests for concurrent authentication requests targeting the same SUPI.

### Prior art / non-duplication note

Known related issues appear to be different:

- CVE-2026-33063 / GHSA-4jrw-92fg-4jwx affects free5GC AUSF, but concerns a nil interface conversion / DoS in `GetSupiFromSuciSupiMap`. It does not cover authentication context overwrite by concurrent requests.
- CVE-2026-44318 affects free5GC BSF and concerns a different concurrency issue in a different NF. It does not cover AUSF `UePool` authentication state keyed by SUPI.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-334q-h5g3-fpxv
- https://github.com/free5gc/free5gc
