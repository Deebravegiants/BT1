# [H] Plane has SSRF via Incomplete IP Validation in Webhook URL Serializer

## Summary
Severity: High
Advisory: GHSA-fpx8-73gf-7x73
CVE: CVE-2026-30242
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-fpx8-73gf-7x73
Type: github-advisory

## Affected
- PyPI: `plane` — affected >=0 <1.2.3

## Details
### Summary
The webhook URL validation in `plane/app/serializers/webhook.py` only checks `ip.is_loopback`, allowing attackers with workspace ADMIN role to create webhooks pointing to private/internal network addresses (`10.x.x.x`, `172.16.x.x`, `192.168.x.x`, `169.254.169.254`, etc.). When webhook events fire, the server makes requests to these internal addresses and stores the response — enabling SSRF with full response read-back.

### Impact
- **Cloud metadata exfiltration**: Access AWS/GCP/Azure instance metadata (IAM credentials, tokens)
- **Internal service scanning**: Probe internal network services not exposed to the internet
- **Data exfiltration via response logs**: Full response body from internal services is stored and returned to the attacker through the webhook logs API
- Bypass vectors: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `0.0.0.0`, `::ffff:` mapped addresses

## References
- https://github.com/makeplane/plane/security/advisories/GHSA-fpx8-73gf-7x73
- https://nvd.nist.gov/vuln/detail/CVE-2026-30242
- https://github.com/makeplane/plane
- https://github.com/makeplane/plane/releases/tag/v1.2.3
