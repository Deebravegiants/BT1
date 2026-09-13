# [M] Uptime Kuma is Missing Authorization Checks on Ping Badge Endpoint, Leaks Ping times of monitors without needing to be on a status page

## Summary
Severity: Medium
Advisory: GHSA-c7hf-c5p5-5g6h
CVE: CVE-2026-32230
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-c7hf-c5p5-5g6h
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=2.0.0 <2.2.0

## Details
## Summary

The `GET /api/badge/:id/ping/:duration?` endpoint in `server/routers/api-router.js` does not verify that the requested monitor belongs to a public group. All other badge endpoints check `AND public = 1` in their SQL query before returning data. The ping endpoint skips this check entirely, allowing unauthenticated users to extract average ping/response time data for private monitors.

## Affected Code

File: `server/routers/api-router.js`, approximately line 304

The ping badge endpoint directly calls `UptimeCalculator.getUptimeCalculator(requestedMonitorId)` without first checking if the monitor is public. Compare with the status badge endpoint (~line 148) which correctly queries:
```sql
SELECT monitor_group.monitor_id FROM monitor_group, `group`
WHERE monitor_group.group_id = `group`.id
AND monitor_group.monitor_id = ?
AND public = 1
```

## Protected vs Vulnerable Endpoints

| Endpoint | Has public=1 check? |
|----------|-------------------|
| /api/badge/:id/status | Yes |
| /api/badge/:id/uptime/:duration? | Yes |
| /api/badge/:id/avg-response/:duration? | Yes |
| /api/badge/:id/cert-exp | Yes |
| /api/badge/:id/response | Yes |
| /api/badge/:id/ping/:duration? | **No — vulnerable** |

## PoC

1. Install Uptime Kuma (tested on latest v2 stable via Docker)
2. Create an HTTP(s) monitor (e.g., monitoring http://localhost:3001)
3. Do NOT add the monitor to any public status page or group
4. Wait for heartbeats to accumulate (~5 minutes)
5. Query unauthenticated:
```bash
curl http://localhost:3001/api/badge/1/status   → returns N/A (correct, monitor is private)
curl http://localhost:3001/api/badge/1/ping/24  → returns "Avg. Ping (24h): 10ms" (LEAKED)
```

## Impact

An unauthenticated attacker can:
- Enumerate private monitor IDs
- Extract average response time data for private monitors
- Infer existence and reachability of internal monitored services

## Suggested Fix

Add the same public monitor check before the UptimeCalculator call:
```javascript
let publicMonitor = await R.getRow(`
    SELECT monitor_group.monitor_id FROM monitor_group, \`group\`
    WHERE monitor_group.group_id = \`group\`.id
    AND monitor_group.monitor_id = ?
    AND public = 1
`, [requestedMonitorId]);

if (!publicMonitor) {
    badgeValues.message = "N/A";
    badgeValues.color = badgeConstants.naColor;
}
```

<img width="1228" height="710" alt="Screenshot 2026-02-24 at 4 49 40 PM" src="https://github.com/user-attachments/assets/80aeae2d-be08-449f-8b39-c50da7aaedba" />

<img width="1271" height="770" alt="File Alons til View He" src="https://github.com/user-attachments/assets/d50c9a00-282a-4b79-b5e1-f77afde9223a" />

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-c7hf-c5p5-5g6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-32230
- https://github.com/louislam/uptime-kuma/issues/7038
- https://github.com/louislam/uptime-kuma/issues/7135
- https://github.com/louislam/uptime-kuma/commit/303a609c05d0b174a5045c90f53c2b557d4febae
- https://github.com/louislam/uptime-kuma
- https://github.com/louislam/uptime-kuma/releases/tag/2.2.0
