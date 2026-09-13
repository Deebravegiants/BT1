# [M] Nezha's private services (`EnableShowInService: false`) are enumerable via per-server endpoints, leaking name and timing data

## Summary
Severity: Medium
Advisory: GHSA-vrmh-5mmx-hjwx
CVE: CVE-2026-49397
CWE: CWE-200, CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-vrmh-5mmx-hjwx
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=2.0.0 <2.0.14

## Details
# Private services (`EnableShowInService: false`) are enumerable via per-server endpoints, leaking name and timing data

**CWE**: CWE-285 (Improper Authorization) via CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor) and CWE-863 (Incorrect Authorization — inconsistent gating across data-reader paths)

**CVSS v3.1**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` → 5.3 (Medium)

## Summary

The `EnableShowInService` flag on a `Service` is meant to gate that service's visibility from the public dashboard. The main service-listing endpoint (`GET /api/v1/service` → `showService`) correctly filters services with `EnableShowInService: false` via `ServiceSentinel.CopyStats()` (`service/singleton/servicesentinel.go:421-438`). However, two adjacent reader endpoints retrieve service objects through code paths that do not honor the same flag:

- `GET /api/v1/server/:id/service` (`listServerServices`) iterates `ServiceSentinel.GetSortedList()` (which returns every service regardless of visibility) and emits service ID, name, and timing data for any service monitoring the queried server.
- `GET /api/v1/service/:id/history` (`getServiceHistory`) calls `ServiceSentinel.Get(serviceID)` directly and emits the service name (and aggregated per-server stats for servers the viewer can see).

Both endpoints are mounted on the `optionalAuth` group, so an unauthenticated visitor can enumerate hidden services as long as they can guess a public server ID (linear scan over a small numeric ID space) or a service ID (likewise). The service owner's intent — "hide this from the public" via `EnableShowInService: false` — is silently bypassed.

## Affected

- nezha `master` at HEAD `636f4a99e6c3d8d75f17fdf7ad55d4ee0f73f1c0` (the audit checkout)
- All recent 2.x releases that share this code path (post the `EnableShowInService` filter introduction at `CopyStats`)

## Vulnerability details

### [A] — single-source-of-truth filter exists at the listing site

`service/singleton/servicesentinel.go:421-438`:

```go
func (ss *ServiceSentinel) CopyStats() map[uint64]model.ServiceResponseItem {
    var stats map[uint64]*serviceResponseItem
    copier.Copy(&stats, ss.LoadStats())

    sri := make(map[uint64]model.ServiceResponseItem)
    for k, service := range stats {
        if !service.service.EnableShowInService {       // [A] filter here
            delete(stats, k)
            continue
        }
        service.ServiceName = service.service.Name
        sri[k] = service.ServiceResponseItem
    }
    return sri
}
```

`CopyStats()` is the only reader that respects `EnableShowInService`. `Get()` and `GetSortedList()` immediately below it return the raw services with no such filter:

```go
func (ss *ServiceSentinel) Get(id uint64) (s *model.Service, ok bool) {
    ss.servicesLock.RLock(); defer ss.servicesLock.RUnlock()
    s, ok = ss.services[id]
    return                                              // [A'] no EnableShowInService check
}
```

### [B] — `listServerServices` iterates `GetSortedList()` and emits hidden services

`cmd/dashboard/controller/service.go:258-340` (`GET /api/v1/server/:id/service`):

```go
func listServerServices(c *gin.Context) ([]*model.ServiceInfos, error) {
    // ... server existence + userCanViewServer check ...
    services := singleton.ServiceSentinelShared.GetSortedList()      // [B] all services, no filter

    for _, service := range services {
        if service.Cover == model.ServiceCoverAll {
            if service.SkipServers[serverID] { continue }
        } else {
            if !service.SkipServers[serverID] { continue }
        }
        // ... fetch history ...
        infos := &model.ServiceInfos{
            ServiceID:   service.ID,
            ServerID:    serverID,
            ServiceName: service.Name,                  // [B'] leaked
            ServerName:  server.Name,
            // ... timing data ...
        }
        result = append(result, infos)
    }
    return result, nil
}
```

The DB-fallback path at `queryServerServicesFromDB` (`service.go:340-`) has the same structure: iterates `services` (the same `GetSortedList()` output) and emits ServiceName for any service monitoring `serverID`.

### [C] — `getServiceHistory` returns the service name for any ID

`cmd/dashboard/controller/service.go:126-180` (`GET /api/v1/service/:id/history`):

```go
func getServiceHistory(c *gin.Context) (*model.ServiceHistoryResponse, error) {
    serviceID, _ := strconv.ParseUint(c.Param("id"), 10, 64)
    service, ok := singleton.ServiceSentinelShared.Get(serviceID)   // [C] no filter
    if !ok || service == nil {
        return nil, singleton.Localizer.ErrorT("service not found")
    }
    // period restriction for guests (1d only) — but the service exists,
    // and ServiceName is set unconditionally:
    response := &model.ServiceHistoryResponse{
        ServiceID:   serviceID,
        ServiceName: service.Name,                       // [C'] leaked
        Servers:     make([]model.ServerServiceStats, 0),
    }
    // ... per-server data is filtered via userCanViewServer — that part is correct ...
    return response, nil
}
```

The per-server data inside the response IS correctly filtered via `userCanViewServer`. The service NAME is not.

### The mismatch

[A] (`CopyStats`) gates by `EnableShowInService` because that's the listing endpoint's contract. [A'] (`Get`) / `GetSortedList()` return the raw data because they're "internal" accessors. But [B] and [C] are public-reachable endpoints that use those raw accessors and emit identifying information about services the owner marked as private. The visibility flag exists; it just isn't enforced at every reader of the same data.

A correct guard would either:
- Move the `EnableShowInService` filter into `Get()` / `GetSortedList()` themselves, gated by "caller is admin or service owner"
- Re-check `EnableShowInService` at every endpoint that emits service identity (name/id/timing)

## Proof of concept

Setup (any nezha 2.x deployment):
1. User A (member) creates a Service "Internal-CRM-Health" with `EnableShowInService: false`, monitoring server `S` which is public (`HideForGuest: false`).
2. The service does not appear in `GET /api/v1/service` (the main listing correctly hides it).

Enumeration as an unauthenticated guest:

```bash
# Find services that monitor server S
curl -s 'https://nezha.example/api/v1/server/'"$S_ID"'/service'
# →
# {"success":true,"data":[
#   {"service_id":42,"server_id":1,"service_name":"Internal-CRM-Health","server_name":"web-01",
#    "display_index":0,"created_at":[...],"avg_delay":[...]}
# ]}
#
# Hidden service is leaked: ID, name, and per-server timing data are all visible.
```

Confirmation via the second endpoint:

```bash
curl -s 'https://nezha.example/api/v1/service/42/history?period=1d'
# →
# {"success":true,"data":{
#   "service_id":42,
#   "service_name":"Internal-CRM-Health",  ← leaked even for direct ID lookup
#   "servers":[]                            ← per-server data correctly hidden
# }}
```

A scripted enumeration over public server IDs (a low-cardinality numeric space — typical nezha deployments have <1000 servers) trivially recovers the full set of hidden services that monitor any public server, along with their names and timing patterns.

## Impact

### Direct

Service names in nezha deployments are frequently descriptive of the underlying business asset they monitor: `"Production CRM Monitor"`, `"Internal Wiki Health"`, `"Backup-Vault Connectivity"`, `"Stripe Webhook Latency"`. The leak therefore:

- **Discloses the existence and purpose of internal services** that the owner explicitly hid from the public dashboard.
- **Exposes timing/latency data** for the monitored relationship between a private service and any public server it touches — sufficient for a competitor or attacker to infer business activity patterns, outage windows, and probable backend topology.
- **Confirms presence/absence of a service ID** via the second endpoint — an oracle that lets an unauthenticated visitor enumerate the service-id namespace and learn the deployment's service count and naming convention even when no public servers exist as enumeration vectors.

### Indirect / second-order

- **Affects multi-tenant public dashboards**: nezha is frequently deployed as a public status page with a private "internal" tier in the same dashboard. The bypass collapses the privacy boundary between these tiers.
- **Composability with prior advisories**: the recent fixes for `GHSA-rxf6-wjh4-jfj6` (cross-user trigger-task firing), `GHSA-hvv7-hfrh-7gxj` (WS server-stream cross-tenant leak), and `GHSA-4g6j-g789-rghm` (forged monitor results) all address the cross-tenant visibility model. This finding is a sibling that closes one more reader gap in the same model.

## Suggested fix

Either of:

1. **Centralize the filter in `ServiceSentinel`** — change `Get(id)` and `GetSortedList()` to accept the `*gin.Context` (or a viewer context) and apply the `EnableShowInService` filter plus an admin-or-owner override. This guarantees every reader inherits the gate:

   ```go
   func (ss *ServiceSentinel) GetForViewer(c *gin.Context, id uint64) (*model.Service, bool) {
       s, ok := ss.Get(id)
       if !ok { return nil, false }
       if !s.EnableShowInService && !callerIsAdminOrOwns(c, s) {
           return nil, false
       }
       return s, true
   }
   ```

2. **Recheck at every endpoint that emits service identity** — add the EnableShowInService + ownership check at the top of `listServerServices`, `getServiceHistory`, and anywhere else `GetSortedList()`/`Get()` results flow to a response. More surgical but easier to miss next time.

Option (1) is symmetric with how `userCanViewServer` centralizes the server-visibility decision; the same pattern at the service layer would close this class once.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-vrmh-5mmx-hjwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-49397
- https://github.com/nezhahq/nezha
