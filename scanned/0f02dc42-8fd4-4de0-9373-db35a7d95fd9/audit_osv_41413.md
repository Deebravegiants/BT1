# [C] AIT-GUI < 2.5.1 Missing Authentication via Sessions.create()

## Summary
Severity: Critical
Advisory: CVE-2026-60112
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-60112
Type: osv

## Details
AMMOS Instrument Toolkit (AIT) GUI before 2.5.1 contains a missing authentication vulnerability that allows any unauthenticated network attacker to obtain a valid session and issue arbitrary spacecraft commands by calling Sessions.create() without any credential check. Attackers can exploit the unauthenticated session issuance in Sessions.create() and subsequently invoke handle_cmd() to forward arbitrary commands directly to the AIT command bus without any authentication gate between session creation and command dispatch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60112.json
- https://github.com/NASA-AMMOS/AIT-GUI/releases/tag/2.5.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-60112
- https://www.vulncheck.com/advisories/ait-gui-missing-authentication-via-sessions-create
- https://github.com/NASA-AMMOS/AIT-GUI/blob/2.5.1/CHANGELOG.md
- https://github.com/NASA-AMMOS/AIT-GUI/commit/beb8fc0813eded89f985d3eb9a73535dd327726d
- https://github.com/NASA-AMMOS/AIT-GUI
