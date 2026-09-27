# [C] Soft Serve is vulnerable to SSRF through its Webhooks

## Summary
Severity: Critical
Advisory: GHSA-vwq2-jx9q-9h9f
CVE: CVE-2025-64522
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-11-10
Source: https://github.com/advisories/GHSA-vwq2-jx9q-9h9f
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.11.1

## Details
SUMMARY

We have identified and verified an SSRF vulnerability where webhook URLs are not validated, allowing repository administrators to create webhooks targeting internal services, private networks, and cloud metadata endpoints.


AFFECTED COMPONENTS (VERIFIED)

1. Webhook Creation (pkg/ssh/cmd/webhooks.go:125)
2. Backend CreateWebhook (pkg/backend/webhooks.go:17)
3. Backend UpdateWebhook (pkg/backend/webhooks.go:122)
4. Webhook Delivery (pkg/webhook/webhook.go:97)

IMPACT

This vulnerability allows repository administrators to perform SSRF attacks, potentially enabling:

a) Cloud Metadata Theft - Access AWS/Azure/GCP credentials via 169.254.169.254
b) Internal Network Access - Target localhost and private networks (10.x, 192.168.x, 172.16.x)
c) Port Scanning - Enumerate internal services via response codes and timing
d) Data Exfiltration - Full HTTP responses stored in webhook delivery logs
e) Internal API Access - Call internal admin panels and Kubernetes endpoints

PROOF OF CONCEPT

Simple example demonstrating localhost access:

```sh
ssh localhost webhook create my-repo http://127.0.0.1:8080/internal \
    --events push --active
```

then push to trigger.

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-vwq2-jx9q-9h9f
- https://nvd.nist.gov/vuln/detail/CVE-2025-64522
- https://github.com/charmbracelet/soft-serve/commit/bb73b9a0eea0d902da4811420535842a4f9aae3b
- https://github.com/charmbracelet/soft-serve
- https://github.com/charmbracelet/soft-serve/releases/tag/v0.11.1
