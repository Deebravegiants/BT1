# [H] PraisonAI Has Unauthenticated SSE Event Stream that Exposes All Agent Activity in A2U Server

## Summary
Severity: High
Advisory: GHSA-f292-66h9-fpmf
CVE: CVE-2026-39889
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-f292-66h9-fpmf
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.115

## Details
The A2U (Agent-to-User) event stream server in PraisonAI exposes all agent activity without authentication. This is a separate component from the gateway server fixed in CVE-2026-34952.

The create_a2u_routes() function registers the following endpoints with NO authentication checks:
- GET  /a2u/info       — exposes server info and stream names
- POST /a2u/subscribe  — creates event stream subscription
- GET  /a2u/events/{stream_name} — streams ALL agent events
- GET  /a2u/events/sub/{id}     — streams events for subscription
- GET  /a2u/health     — health check


An unauthenticated attacker can:
1. POST /a2u/subscribe → receive subscription_id
2. GET /a2u/events/sub/{subscription_id} → receive live SSE stream 
   of all agent events including responses, tool calls, and thinking

This exposes sensitive agent activity including responses, internal  reasoning, and tool call arguments to any network attacker.

<img width="1512" height="947" alt="image" src="https://github.com/user-attachments/assets/3438f3ea-75ec-4978-9dd9-d9a6da42c248" />

<img width="1512" height="571" alt="image" src="https://github.com/user-attachments/assets/ee3313f6-f522-48f7-9c06-e5e265c6aeb4" />


[1] POST /a2u/subscribe (no auth token)
    Status: 200
    Response: {"subscription_id":"sub-a1ad8a6edd8b","stream_name":"events",
    "stream_url":"http://testserver/a2u/events/sub-a1ad8a6edd8b"}
    Got subscription_id: sub-a1ad8a6edd8b

[2] GET /a2u/info (no auth token)
    Status: 200
    Response: {"name":"A2U Event Stream","version":"1.0.0",
    "streams":["events"],"event_types":["agent.started","agent.thinking",
    "agent.tool_call","agent.response","agent.completed","agent.error"]}

[3] GET /a2u/health (no auth token)  
    Status: 200
    Response: {"status":"healthy","active_subscriptions":1,"active_streams":1}


Impact: Attacker can subscribe and receive ALL agent events including responses, tool calls, and internal reasoning in real-time

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-f292-66h9-fpmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-39889
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.115
