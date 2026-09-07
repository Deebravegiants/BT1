# [M] Umbraco Backoffice API Allows Unauthorized Modification of Domain Data

## Summary
Severity: Medium
Advisory: GHSA-fpvf-fvp5-996r
CVE: CVE-2026-31832
CWE: CWE-639
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-fpvf-fvp5-996r
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <16.5.1
- NuGet: `Umbraco.Cms` — affected >=17.0.0 <17.2.2

## Details
### Description
A broken object-level authorization vulnerability exists in a backoffice API endpoint that allows authenticated users to assign domain-related data to content nodes without proper authorization checks.

The issue is caused by insufficient authorization enforcement on the affected API endpoint, whereby via an API call, domains can be set on content nodes that the editor does not have permission to access (either via user group privileges or start nodes).

### Impact
An attacker can modify domain configurations for content nodes they are not permitted to edit. This may result in malicious or unintended routing behaviour, service disruption, and potential disclosure of configuration-related information.

### Patches
The issue is patched in 16.5.1 and 17.2.2.

### Workarounds
There is no workaround other than upgrading.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-fpvf-fvp5-996r
- https://nvd.nist.gov/vuln/detail/CVE-2026-31832
- https://github.com/umbraco/Umbraco-CMS
