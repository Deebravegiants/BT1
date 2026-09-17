# [M] CVE-2026-47357

## Summary
Severity: Medium
Advisory: CVE-2026-47357
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-47357
Type: osv

## Details
Terrascan v1.18.3 and prior are vulnerable to Server-Side Request Forgery (SSRF) via the remote_url parameter in the remote directory scan endpoint (POST /v1/{iac}/{iacVersion}/{cloud}/remote/dir/scan) when running in server mode. An unauthenticated remote attacker can supply an attacker-controlled HTTP URL as remote_url with remote_type set to "http". The URL is passed directly to hashicorp/go-getter (v1.7.5) without validation. Go-getter's HttpGetter supports the X-Terraform-Get response header, allowing the attacker's server to redirect the download to a file:// URL, enabling local file read. Additionally, HttpGetter has Netrc set to true, causing it to read ~/.netrc and send stored credentials to attacker-controlled hostnames. This affects deployments running terrascan in server mode (terrascan server), which binds to 0.0.0.0 with no authentication. Note: Terrascan was archived in August 2023 and no patch will be released.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47357.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47357
- https://github.com/tenable/terrascan
