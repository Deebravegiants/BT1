# [C] FireFighter has unauthenticated SSRF in its Raid jira_bot endpoint that allows IAM credential theft

## Summary
Severity: Critical
Advisory: GHSA-fqvv-jvhr-g5jc
CVE: CVE-2026-42864
CWE: CWE-306, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-fqvv-jvhr-g5jc
Type: github-advisory

## Affected
- PyPI: `firefighter-incident` — affected >=0 <0.0.54

## Details
### Impact
  The `POST /api/v2/firefighter/raid/jira_bot` endpoint (`CreateJiraBotView`) is
  reachable without authentication (`permission_classes = [permissions.AllowAny]`).
  Its `attachments` payload is fetched server-side via `httpx.get()` with no URL
  validation, then uploaded as an attachment on the Jira ticket that gets created.

  An unauthenticated caller able to reach the ingress can coerce the pod into
  fetching arbitrary URLs — including the cloud metadata endpoint at
  `http://169.254.169.254/` — and exfiltrate the response as a Jira attachment.

  On EC2/EKS deployments that do not enforce IMDSv2, this allows theft of the
  temporary AWS credentials attached to the pod's IAM role. The docstring on the
  view claims a Bearer token is required, but the code does not enforce it.

  Affected code paths:
  - `src/firefighter/raid/views/__init__.py` — `CreateJiraBotView`
  - `src/firefighter/raid/serializers.py` — `LandbotIssueRequestSerializer.attachments`
  - `src/firefighter/raid/client.py` — `RaidJiraClient.add_attachments_to_issue`

  ### Patches
  Fixed in `firefighter-incident` `0.0.54`:
  - `CreateJiraBotView` now enforces `BearerTokenAuthentication` + `IsAuthenticated`.
  - `attachments` URLs are validated: http(s) scheme only, max 10 URLs, rejection
    of any host resolving to a private, loopback, link-local, reserved, multicast
    or unspecified IP (IPv4 and IPv6).
  - Fixes an unrelated `KeyError('attachments')` surfaced during regression testing.

  Users should upgrade to `0.0.54` or later.

  ### Workarounds
  Until upgrade is possible, any one of the following blocks end-to-end exploitation:
  - Restrict ingress access to `/api/v2/firefighter/raid/jira_bot` to trusted
    networks only (VPN, internal load balancer).
  - Rotate or revoke the Jira API token configured as `RAID_JIRA_API_PASSWORD`;
    this breaks `jira.create_issue()` before the vulnerable attachment fetch is
    reached (legitimate traffic is also blocked — emergency mitigation only).
  - Enforce IMDSv2 with `HttpPutResponseHopLimit=1` on EC2/EKS nodes. This does
    not fix the SSRF itself but neutralises the IAM-credential-theft path.

  ### Resources
  - CWE-918: Server-Side Request Forgery
  - CWE-306: Missing Authentication for Critical Function

## References
- https://github.com/ManoManoTech/firefighter-incident/security/advisories/GHSA-fqvv-jvhr-g5jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42864
- https://github.com/ManoManoTech/firefighter-incident/commit/2586679e6f32c12d223668b73e98f4c4de7b771f
- https://github.com/ManoManoTech/firefighter-incident
