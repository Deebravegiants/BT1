# [C] DNS NuGet package uses insufficiently random values

## Summary
Severity: Critical
Advisory: GHSA-g3wc-xv93-445q
CVE: CVE-2021-4248
CWE: CWE-330
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-18
Source: https://github.com/advisories/GHSA-g3wc-xv93-445q
Type: github-advisory

## Affected
- NuGet: `DNS` — affected >=0 <7.0.0

## Details
A vulnerability was found in kapetan dns up to 6.1.0. It has been rated as problematic. Affected by this issue is some unknown functionality of the file DNS/Protocol/Request.cs. The manipulation leads to insufficient entropy in prng. The attack may be launched remotely. Upgrading to version 7.0.0 can address this issue. The name of the patch is cf7105aa2aae90d6656088fe5a8ee1d5730773b6. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216188.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4248
- https://github.com/kapetan/dns/pull/88
- https://github.com/kapetan/dns/commit/cf7105aa2aae90d6656088fe5a8ee1d5730773b6
- https://github.com/kapetan/dns
- https://github.com/kapetan/dns/releases/tag/v7.0.0
- https://vuldb.com/?id.216188
