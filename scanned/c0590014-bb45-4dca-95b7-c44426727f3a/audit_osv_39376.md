# [C] Dokku: Host RCE via Maliciously Named OpenResty Include Files Injected Through eval

## Summary
Severity: Critical
Advisory: CVE-2026-45406
Aliases: GHSA-ggqh-98fj-8mg9
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-45406
Type: osv

## Details
Dokku is a docker-powered PaaS. Prior to 0.38.2, the openresty-vhosts plugin copies files from an app's openresty/http-includes/ git repository directory to the host and then interpolates their filenames, unescaped, into a single-quoted shell string that is later parsed by eval. A filename containing a single quote breaks the quoting and allows command substitution to execute arbitrary commands on the host as the dokku user during the app's next deploy. This vulnerability is fixed in 0.38.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45406.json
- https://github.com/dokku/dokku/security/advisories/GHSA-ggqh-98fj-8mg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45406
- https://github.com/dokku/dokku/pull/8588
