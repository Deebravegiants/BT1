# [M] Hermes WebUI < 0.51.269 Profile Isolation Bypass via sessions search

## Summary
Severity: Medium
Advisory: CVE-2026-49956
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49956
Type: osv

## Details
Hermes WebUI before version 0.51.269 contains a profile isolation bypass vulnerability that allows authenticated users to access data belonging to other profiles by querying the session search endpoint without active-profile filtering. Attackers can send requests to the sessions search handler to retrieve session titles and transcript message content from profiles other than their own active profile.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49956.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.269
- https://nvd.nist.gov/vuln/detail/CVE-2026-49956
- https://www.vulncheck.com/advisories/hermes-webui-profile-isolation-bypass-via-sessions-search
- https://github.com/nesquena/hermes-webui/pull/3646
- https://github.com/nesquena/hermes-webui/pull/3672
- https://github.com/nesquena/hermes-webui/commit/2c7b530071bb29ae4184e83e33be5799d529568e
- https://github.com/nesquena/hermes-webui
