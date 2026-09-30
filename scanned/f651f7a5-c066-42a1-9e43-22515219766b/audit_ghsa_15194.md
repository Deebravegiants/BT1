# [H] TrueLayer.Client SSRF when fetching payment or payment provider

## Summary
Severity: High
Advisory: GHSA-67m4-qxp3-j6hh
CVE: CVE-2024-23838
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-67m4-qxp3-j6hh
Type: github-advisory

## Affected
- NuGet: `TrueLayer.Client` — affected >=0 <1.6.0

## Details
### Impact
The vulnerability could potentially allow a malicious actor to gain control over the destination URL of the HttpClient used in the API classes. For applications using the SDK, requests to unexpected resources on local networks or to the internet could be made which could lead to information disclosure.

### Patches
Versions of TrueLayer.Client `v1.6.0` and later are not affected.

### Workarounds
The issue can be mitigated by having strict egress rules limiting the destinations to which requests can be made, and applying strict validation to any user input passed to the TrueLayer.Client library.

## References
- https://github.com/TrueLayer/truelayer-dotnet/security/advisories/GHSA-67m4-qxp3-j6hh
- https://nvd.nist.gov/vuln/detail/CVE-2024-23838
- https://github.com/TrueLayer/truelayer-dotnet/commit/75e436ed5360faa73d6e7ce3a9903a3c49505e3e
- https://github.com/TrueLayer/truelayer-dotnet
