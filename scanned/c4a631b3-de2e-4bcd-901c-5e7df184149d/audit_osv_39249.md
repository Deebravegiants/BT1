# [M] EMQX: Stale plugins allow grants amplify a compromised admin/API key to remote code execution

## Summary
Severity: Medium
Advisory: CVE-2026-44725
Aliases: GHSA-cp9x-5qwc-fj6r
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-44725
Type: osv

## Details
EMQX is a scalable and reliable MQTT broker for AI, IoT, IIoT, and connected vehicles. Prior to versions 5.8.11, 5.9.3, 5.10.4, 6.0.3, 6.1.2, and 6.2.1, the plugin-install REST API and dashboard upload accepted stale grants created with emqx ctl plugins allow because there was no five-minute grant lifetime or SHA-256 package binding. An attacker with a compromised dashboard administrator credential or API key with plugin-install permission who finds a stale allowed name and version can upload attacker-controlled bytes under the allowed .tar.gz filename through POST /api/v5/plugins/install or the dashboard plugin upload. The broker then installs and runs attacker-controlled Erlang code with the privileges of the EMQX process. This issue is fixed in versions 5.8.11, 5.9.3, 5.10.4, 6.0.3, 6.1.2, and 6.2.1.

## References
- https://github.com/emqx/emqx/releases/tag/6.0.3
- https://github.com/emqx/emqx/releases/tag/6.1.2
- https://github.com/emqx/emqx/releases/tag/6.2.1
- https://github.com/emqx/emqx/releases/tag/e5.10.4
- https://github.com/emqx/emqx/releases/tag/e5.8.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44725.json
- https://github.com/emqx/emqx/security/advisories/GHSA-cp9x-5qwc-fj6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44725
- https://github.com/emqx/emqx/commit/2f926359fa847dd9928a8e94d3e342f5621806f4
- https://github.com/emqx/emqx/commit/efa1ca1bef1517f1f87e1d562f8db8750b6d6ce3
- https://github.com/emqx/emqx/pull/17200
- https://github.com/emqx/emqx/pull/17201
