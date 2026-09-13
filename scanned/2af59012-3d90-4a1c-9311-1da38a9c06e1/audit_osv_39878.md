# [M] OpenReception's bootstrap booking flow allows unauthenticated booking on isPublic=false channels

## Summary
Severity: Medium
Advisory: CVE-2026-48076
Aliases: GHSA-3658-3j75-p5j3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48076
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. The new-client booking flow in versions 1.0.1 and prior consists of three calls: `bootstrap-challenge` (returns a 16-bit PoW challenge with `difficulty=4` leading hex zeroes), `bootstrap-verify` (validates the PoW and issues a Bearer booking access token), and `create-new-client` (consumes the token and creates the tunnel and first appointment). The token correctly binds to `tenantId`, `tunnelId`, `clientPublicKey`, and `emailHash`, but never to `channelId`. The `bootstrap-challenge` request schema does not even accept a `channelId`, and the issued token's payload contains no channel information. Independently, the service function `createNewClientWithAppointment` checks only `channel.archived = false`. The `channel.isPublic` check that protects `addAppointmentToTunnel` is missing in the new-client path. The combination means: an attacker completes the bootstrap flow normally (16-bit PoW, completes in well under one second on commodity hardware, no rate limiting beyond the throttle store), receives a valid booking access token, and then submits the `create-new-client` payload with `channelId` pointing to a private (`isPublic = false`) channel. The booking lands as `CONFIRMED` if the target channel has `requiresConfirmation = false` (the default), otherwise as `NEW`. The patient-facing UI does not list private channels in its picker (`/api/public/channels` correctly filters `isPublic = true`), so the channel ID must be obtained out of band. The companion finding V-10 (schedule endpoint discloses private channels) provides exactly that: a single unauthenticated GET reveals every private channel ID for any tenant. V-10 plus V-11 together make private channels fully reachable to anonymous attackers. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48076.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-3658-3j75-p5j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-48076
