# [M] FUXA provides guest and invalid-token access to protected read APIs in secure mode

## Summary
Severity: Medium
Advisory: GHSA-r9g5-7q8j-958c
CVE: CVE-2026-47718
CWE: CWE-287, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-r9g5-7q8j-958c
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=1.3.0-2773 <1.3.1

## Details
### Summary

  When `secureEnabled=true`, FUXA `1.3.0-2773` still allows guest and invalid-token requests to read project, alarms, and scheduler APIs.

  ### Details

  In secure mode, requests with no token or an explicitly invalid token were still able to access protected read endpoints.

  Confirmed behavior:

  - guest `GET /api/project` returned `200 OK`
  - invalid-token requests to `/api/project` also returned successful responses containing project data
  - guest and invalid-token requests also returned `200 OK` on:
    - `/api/alarms`
    - `/api/scheduler`

  Relevant code paths identified during analysis:

  - `server/api/jwt-helper.js`
    - `verifyToken()` converts missing-token or invalid-token states into guest context instead of rejecting the request
  - `server/api/projects/index.js`
  - `server/api/alarms/index.js`
  - `server/api/scheduler/index.js`

  These handlers accepted the guest context and returned sensitive data in secure mode.

  ### PoC

  Tested only against isolated local lab instances under the original tester's control. No production, customer, shared, or third-party systems were involved.

  Reproduction:

  1. Start FUXA `1.3.0-2773`.
  2. Set `secureEnabled=true`.
  3. Send unauthenticated requests to:
     - `GET /api/project`
     - `GET /api/alarms`
     - `GET /api/scheduler?id=test`
  4. Observe `200 OK` responses.
  5. Send the same requests with an explicitly invalid `x-access-token` value.
  6. Observe the same successful responses.

 The exact HTTP requests and local PoC script used for confirmation can be provided upon request.

  ### Impact

  This is an authentication/authorization weakness in secure mode.

  Impact includes:

 - project metadata disclosure
 - alarms disclosure
 - scheduler information disclosure
 - assistance in reconnaissance/follow-on attacks

  Operators who believe secure mode protects these APIs are impacted.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-r9g5-7q8j-958c
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.1
