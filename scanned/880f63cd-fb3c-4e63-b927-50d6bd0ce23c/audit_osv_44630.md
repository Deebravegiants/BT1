# [M] Label Studio through 1.23.0 SSRF via Unvalidated Webhook URL

## Summary
Severity: Medium
Advisory: CVE-2026-85179
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85179
Type: osv

## Details
Label Studio through 1.23.0 fails to validate webhook URLs, allowing authenticated users to dispatch requests to internal services including RFC 1918 addresses and cloud metadata endpoints. Attackers can create webhooks targeting private networks and exfiltrate annotation data by enabling payload transmission in outbound requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85179.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85179
- https://www.vulncheck.com/advisories/label-studio-through-1.23.0-ssrf-via-unvalidated-webhook-url
- https://github.com/HumanSignal/label-studio/issues/9801
- https://github.com/HumanSignal/label-studio/commit/2c1c1d6472153032af8ed399168f814bea854e3e
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.23.0/label_studio/webhooks/utils.py
