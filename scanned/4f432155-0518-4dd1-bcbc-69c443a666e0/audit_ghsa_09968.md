# [H] monetr: Server-side request forgery in Lunch Flow link creation and refresh

## Summary
Severity: High
Advisory: GHSA-29v9-frvh-c426
CVE: CVE-2026-41644
CWE: CWE-209, CWE-770, CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-29v9-frvh-c426
Type: github-advisory

## Affected
- Go: `github.com/monetr/monetr` — affected >=0 <1.12.5

## Details
### Impact

A server-side request forgery (SSRF) vulnerability in monetr's Lunch Flow integration allowed any authenticated user on
a self-hosted instance to cause the monetr server to issue HTTP GET requests to arbitrary URLs supplied by the caller,
with the response body from non-200 upstream responses reflected back in the API error message.

The URL validator on `POST /api/lunch_flow/link` only checked the URL scheme and rejected query parameters; it did not
filter loopback, RFC1918, link-local, or cloud-provider metadata addresses. The outbound HTTP client read the response
body via an unbounded `io.ReadAll`, and the controller intentionally surfaced the resulting error (which contained the
upstream body) as the JSON `error` field of the API response.

**Who is affected:** self-hosted monetr deployments running the default configuration. Out of the box,
`LunchFlow.Enabled=true`, `AllowSignUp=true`, and billing is not enforced, so any user who can register on the instance
can reach the vulnerable endpoint. Deployments running in a cloud environment where instance metadata is reachable from
the pod (e.g. AWS EC2 without IMDSv2 enforced) expand the impact to include potential exposure of instance metadata
through the reflected error body.

**Who is NOT affected:** the hosted `my.monetr.app` service, which runs with `LunchFlow.Enabled=false`. Self-hosted
operators who had already disabled public sign-up (`MONETR_ALLOW_SIGN_UP=false`) substantially reduce their exposure
since only operator-trusted users can reach the endpoint.

A secondary denial-of-service vector also existed: because the outbound response body was read with no size cap, an
attacker-influenced upstream could return a multi-GB body that monetr would fully buffer into memory.

### Patches

Fixed in monetr `v1.12.5`. Users should upgrade to this release or later.

The fix introduces a new config field `LunchFlow.AllowedApiUrls` (a list of permitted Lunch Flow API URLs) with a
default of `["https://lunchflow.app/api/v1"]`. URLs outside the allowlist are rejected both at link-creation time and at
client-construction time, with a server-side warning log on rejection. Response body reads are capped at 10 MiB for both
success and error paths. The UI renders the API URL field as a disabled pre-filled input when a single URL is allowed,
or a dropdown when multiple are allowed, so operators who need to use a staging or self-hosted Lunch Flow API opt in
explicitly via config.

**Upgrade note for self-hosters with a custom Lunch Flow URL:** if your existing `LunchFlowLink` records point at a URL
other than `https://lunchflow.app/api/v1`, set your `lunchFlow.allowedApiUrls` in your yaml config to include your
custom URL before upgrading. Otherwise existing links will fail on next refresh or sync with a `"Rejected Lunch Flow API
URL that is not in the configured allowlist"` warning in the server log.

### Workarounds

For operators who cannot upgrade immediately, any of the following materially reduces or eliminates exposure:

- **Disable public sign-up:** set `MONETR_ALLOW_SIGN_UP=false` so only operator-trusted users can reach the vulnerable
endpoint. Recommended in general for internet-exposed self-hosted deployments.
- **Disable Lunch Flow entirely:** set `lunchFlow.enabled: false` in your config file. The endpoints will return 404 for
all callers.
- **Network-level egress restriction:** restrict outbound HTTP egress from the monetr pod/container to only
`lunchflow.app` (or whichever legitimate Lunch Flow hosts you use). Blocks the SSRF primitive regardless of
application-layer validation.
- **On AWS EC2 specifically:** enforce IMDSv2 on the instance. This eliminates the cloud-metadata exfil path even if the
SSRF primitive remains reachable.

## References
- https://github.com/monetr/monetr/security/advisories/GHSA-29v9-frvh-c426
- https://nvd.nist.gov/vuln/detail/CVE-2026-41644
- https://github.com/monetr/monetr/pull/3122
- https://github.com/monetr/monetr/commit/c260caa3c573a4a396ec2d264c7641a5d958385b
- https://github.com/monetr/monetr
- https://github.com/monetr/monetr/releases/tag/v1.12.5
