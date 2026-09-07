# [H] Umbraco.Engage.Forms Allows Unauthorized Access to Multiple API Endpoints

## Summary
Severity: High
Advisory: GHSA-86vq-ccwf-rm62
CVE: CVE-2026-27449
CWE: CWE-284, CWE-306, CWE-639
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-86vq-ccwf-rm62
Type: github-advisory

## Affected
- NuGet: `Umbraco.Engage.Forms` — affected >=16.0.0 <16.2.1
- NuGet: `Umbraco.Engage.Forms` — affected >=17.0.0 <17.1.1

## Details
### Description
A vulnerability has been identified in Umbraco Engage where certain API endpoints are exposed without enforcing authentication or authorization checks. The affected endpoints can be accessed directly over the network without requiring a valid session or user credentials. By supplying a user-controlled identifier parameter (e.g., ?id=), an attacker can retrieve sensitive data associated with arbitrary records.

Because no access control validation is performed, the endpoints are vulnerable to enumeration attacks, allowing attackers to iterate over identifiers and extract data at scale.

### Impact
An unauthenticated attacker can retrieve sensitive Engage-related data by directly querying the affected API endpoints. The vulnerability allows arbitrary record access through predictable or enumerable identifiers.

The confidentiality impact is considered high. No direct integrity or availability impact has been identified.

The scope of exposed data depends on the deployment but may include analytics data, tracking data, customer-related information, or other Engage-managed content.

### Patches
The vulnerability affects both v16 and v17. Patches have already been released. Users are advised to update to 16.2.1 or 17.1.1

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/umbraco/Umbraco.Engage.Issues/security/advisories/GHSA-86vq-ccwf-rm62
- https://nvd.nist.gov/vuln/detail/CVE-2026-27449
- https://github.com/umbraco/Umbraco.Engage.Issues
