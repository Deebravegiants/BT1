# [M] OpenReception's unauthenticated add-to-tunnel endpoint accepts arbitrary appointment injections

## Summary
Severity: Medium
Advisory: CVE-2026-48075
Aliases: GHSA-rhp5-vmcx-4qm8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48075
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.0.5, the `add-to-tunnel` endpoint creates a new appointment row in any client tunnel without any caller authentication. A request that supplies any valid `tunnelId` and any valid `emailHash` (the two need not belong to the same tunnel) results in an inserted appointment with `status = "CONFIRMED"`, attacker-controlled ciphertext fields, attacker-controlled date and duration, and an attacker-chosen agent. The endpoint validates only that some tunnel exists with the given `emailHash`, then writes the appointment using the attacker-supplied `tunnelId` directly. The `emailHash` lookup is effectively an existence check on the tenant; it does not authenticate the caller as the owner of the supplied `tunnelId`. Combined with the absence of any session, Authorization header, booking access token, or PoW, this makes the endpoint accept arbitrary appointment writes into arbitrary tunnels. By contrast, the sibling endpoint `create-new-client` (used to bootstrap a brand-new client tunnel) requires a Bearer bootstrap booking access token issued by the bootstrap-challenge / bootstrap-verify flow. The `add-to-tunnel` endpoint, intended for return-clients booking additional appointments, has no equivalent gate. The application's own middleware confirms this is intentional: `add-to-tunnel` is explicitly listed in the apiAuthHandle public-route allowlist alongside the bootstrap and challenge endpoints (which legitimately have no session). Version 1.0.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48075.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-rhp5-vmcx-4qm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48075
- https://github.com/open-reception/appointment-booking-software/commit/4522a44c001782848faff5529d7c1e2be7ac9ef5
