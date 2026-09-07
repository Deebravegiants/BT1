# [M] Terraform Provider  for Linode Debug Logs Vulnerable to Sensitive Information Exposure

## Summary
Severity: Medium
Advisory: GHSA-5rc7-2jj6-mp64
CVE: CVE-2026-27900
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-5rc7-2jj6-mp64
Type: github-advisory

## Affected
- Go: `github.com/linode/terraform-provider-linode/v3` — affected >=0 <3.9.0
- Go: `github.com/linode/terraform-provider-linode/v2` — affected >=0
- Go: `github.com/linode/terraform-provider-linode` — affected >=0

## Details
### Impact
The Terraform Provider for Linode versions prior to v3.9.0 logged sensitive information including some passwords, StackScript content, object storage data, and NodeBalancer TLS keys in debug logs without redaction.

**Important:** Provider debug logging is **not enabled by default**.  
This issue is exposed when debug/provider logs are explicitly enabled (for example in local troubleshooting, CI/CD jobs, or centralized log collection). If enabled, sensitive values may be written to logs and then retained, shared, or exported beyond the original execution environment.

Specifically:
- Instance creation operations logged the full InstanceCreateOptions struct containing RootPass and StackScriptData
- Instance disk creation logged InstanceDiskCreateOptions containing RootPass and StackscriptData
- StackScript update operations logged the complete script content via StackscriptUpdateOptions.Script
- Image share group member creation logged tokens in ImageShareGroupAddMemberOptions.Token
- Object storage operations logged full PutObjectInput structures containing user data
- NodeBalancer config create and update operations logged NodeBalancerConfigCreateOptions and NodeBalancerConfigUpdateOptions containing the SSLKey (TLS private key)

An authenticated user with access to provider debug logs (through log aggregation systems, CI/CD pipelines, or debug output) would thus be able to extract these sensitive credentials.

### Patches
Update to version v3.9.0 or later, which sanitizes debug logs by logging only non-sensitive metadata such as labels, regions, and resource IDs while redacting credentials, tokens, keys, scripts, and other sensitive content.

### Workarounds and Mitigations
- Disable Terraform/provider debug logging or set it to `WARN` level or above
  - To disable the logging, you can unset `TF_LOG_PROVIDER` and `TF_LOG` environment variables
  - Or you can set them to `WARN` or `ERROR` levels to avoid sensitive information logged in `INFO` and `DEBUG` levels.
  - See Terraform docs for details: https://developer.hashicorp.com/terraform/internals/debugging
- Restrict access to existing and historical logs
- Purge/retention-trim logs that may contain sensitive values
- Rotate potentially exposed secrets/credentials, including:
  - Root passwords
  - Image share group tokens
  - TLS private keys/certificates used in NodeBalancer configs
  - StackScript content/secrets if embedded

### Credits
This issue was reported to Terraform by Hasan Sheet via [Akamai's HackerOne Bug Bounty program](https://hackerone.com/akamai).

### Resources
https://github.com/linode/terraform-provider-linode/releases/tag/v3.9.0
https://github.com/linode/terraform-provider-linode/pull/2269
https://github.com/linode/terraform-provider-linode/commit/43a925d826b999f0355de3dc7330c55f496824c0

## References
- https://github.com/linode/terraform-provider-linode/security/advisories/GHSA-5rc7-2jj6-mp64
- https://nvd.nist.gov/vuln/detail/CVE-2026-27900
- https://github.com/linode/terraform-provider-linode/pull/2269
- https://github.com/linode/terraform-provider-linode/commit/43a925d826b999f0355de3dc7330c55f496824c0
- https://github.com/linode/terraform-provider-linode
- https://github.com/linode/terraform-provider-linode/releases/tag/v3.9.0
- http://www.openwall.com/lists/oss-security/2026/02/26/2
