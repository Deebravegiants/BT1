# [M] Flowise Execute Flow function has an SSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9hrv-gvrv-6gf2
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-9hrv-gvrv-6gf2
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0
- npm: `flowise-components` — affected >=0 <3.1.0

## Details
### Summary

The attacker provides an intranet address through the base url field configured in the Execute Flow node 
→ Bypass checkDenyList / resolveAndValidate in httpSecurity.ts (not called)
→ Causes the server to initiate an HTTP request to any internal network address, read cloud metadata, or detect internal network services 

### Details

<img width="1280" height="860" alt="9a52a74e6fe2fd78e4962d1d68057fc2" src="https://github.com/user-attachments/assets/20df0006-9129-4886-8928-16d19a617c23" />

Then initiate the call: 

```
POST /api/v1/prediction/d6739838-d3b3-43d9-86ff-911a3d757a7e HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json
Authorization: Bearer apikey
Content-Length: 17

{"question": "1"}
```

Server received a request:

<img width="1432" height="172" alt="f45c757fec408e13739db068252ff21b" src="https://github.com/user-attachments/assets/d3dfe0f5-83ec-4c79-ab32-754382a68d5f" />

And there is an echo: 

<img width="1280" height="666" alt="fa0caf0deb306cfeeea8fdf8941a287e" src="https://github.com/user-attachments/assets/55a94d25-120b-4e9c-9517-46c2fc2b667f" />

Fix:
Call secureFetch for verification



### Impact

This is a Server-Side Request Forgery (SSRF) vulnerability that may lead to the following risks: 
- Explore Internal Web Applications
- Access sensitive management interfaces
- Leak internal configuration, credentials, or confidential information

This vulnerability significantly increases the risk of internal service enumeration and potential lateral movement in enterprise environments.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-9hrv-gvrv-6gf2
- https://github.com/FlowiseAI/Flowise
