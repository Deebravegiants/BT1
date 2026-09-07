# [M] Pixeldrain API key shared with unverified thirdparty sites

## Summary
Severity: Medium
Advisory: GHSA-f5pf-q7c7-m3vv
CVE: CVE-2026-54254
CWE: CWE-20, CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-f5pf-q7c7-m3vv
Type: github-advisory

## Affected
- PyPI: `cyberdrop-dl-patched` — affected >=8.5.0 <9.14.0

## Details
### Summary

When processing Pixeldrain URLs, `cyberdrop-dl-patched` could send an `Authorization` header that includes the user's API key to unverified hosts.

### Details

Pixeldrain offers several alternative domains in case the user's ISP blocks the primary domain. To support this, requests made by `cyberdrop-dl-patched` are not hardcoded and will use the same host as the input URL for API requests.

`cyberdrop-dl-patched` matches URLs to a crawler based on their host. If the host contains a crawler's supported host as a sub-string, it will match to that crawler. 

An URL from a malicious domain (ex: `https://evil-pixeldrain.com`) would successfully match to the Pixeldrain crawler and `cyberdrop-dl-patched` will blindly use that host for any API request (`https://evil-pixeldrain.com/api`), leaking the user's API key to the malicious actor via the `Authorization` header.

### Impact
Anyone who has setup a Pixeldrain API key with `cyberdrop-dl-patched` and uses `cyberdrop-dl-patched` on sites that could spawn downloads for other sites (ex: forums, Wordpress, Pixeldrain itself, etc...)

### Patches
`cyberdrop-dl-patched`  v9.14.0 fixes this issue by rejecting any Pixedrain URL if the host does not match an official domain __exactly__.

### Workarounds
It's recommended to upgrade `cyberdrop-dl-patched` to version v9.14.0

Anyone who has used a Pixeldrain API key with `cyberdrop-dl-patched` should consider them compromised and delete them from their Pixeldrain account.

## References
- https://github.com/Cyberdrop-DL/cyberdrop-dl/security/advisories/GHSA-f5pf-q7c7-m3vv
- https://github.com/Cyberdrop-DL/cyberdrop-dl/commit/4479555ae3f9d56d7657d6179a5bac3123eb4e2b
- https://docs.pixeldrain.com/questions_and_answers/#alternative-domain-names
- https://github.com/Cyberdrop-DL/cyberdrop-dl
- https://github.com/Cyberdrop-DL/cyberdrop-dl/releases/tag/9.14.0
