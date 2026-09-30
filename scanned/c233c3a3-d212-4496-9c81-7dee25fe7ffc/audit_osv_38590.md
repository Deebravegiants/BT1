# [H] Decidim's comments API allows access to all commentable resources

## Summary
Severity: High
Advisory: CVE-2026-40870
Aliases: GHSA-ghmh-q25g-gxxx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40870
Type: osv

## Details
Decidim is a participatory democracy framework. Starting in version 0.0.1 and prior to versions 0.30.5 and 0.31.1, the root level `commentable` field in the API allows access to all commentable resources within the platform, without any permission checks. All Decidim instances are impacted that have not secured the `/api` endpoint. The `/api` endpoint is publicly available with the default configuration. Versions 0.30.5 and 0.31.1 fix the issue. As a workaround, limit the scope to only authenticated users by limiting access to the `/api` endpoint. This would require custom code or installing the 3rd party module `Decidim::Apiauth`. With custom code, the `/api` endpoint can be limited to only authenticated users. The same configuration can be also used without the `allow` statements to disable all traffic to the the `/api` endpoint. When considering a workaround and the seriousness of the vulnerability, please consider the nature of the platform. If the platform is primarily serving public data, this vulnerability is not serious by its nature. If the platform is protecting some resources, e.g. inside private participation spaces, the vulnerability may expose some data to the attacker that is not meant public. For those who have enabled the organization setting "Force users to authenticate before access organization", the scope of this vulnerability is limited to the users who are allowed to log in to the Decidim platform. This setting was introduced in version 0.19.0 and it was applied to the `/api` endpoint in version 0.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40870.json
- https://github.com/decidim/decidim/security/advisories/GHSA-ghmh-q25g-gxxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40870
