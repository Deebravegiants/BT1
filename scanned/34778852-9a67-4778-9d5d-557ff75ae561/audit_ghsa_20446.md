# [M] Subdomain Takeover in Interactsh server

## Summary
Severity: Medium
Advisory: GHSA-m36x-mgfh-8g78
CVE: CVE-2023-36474
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-m36x-mgfh-8g78
Type: github-advisory

## Affected
- Go: `github.com/projectdiscovery/interactsh` — affected >=0 <1.0.0

## Details
A domain configured with interactsh server was vulnerable to subdomain takeover for specfic subdomain, i.e `app`, Interactsh server before `< 1.0.0` used to create cname entries for `app` pointing to `projectdiscovery.github.io` as default which intended to used for hosting interactsh [web client](https://github.com/projectdiscovery/interactsh-web) using GitHub pages. It turns out to be a security issue with a self-hosted interactsh server in which the user may not have configured a web client but still have a cname entry pointing to GitHub pages, making them vulnerable to subdomain takeover.

This issue was initially reported to us as a subdomain takeover for one of our domains that runs interactsh server by **Melih** at `security@projectdiscovery.io`, and after conducting an internal investigation, we determined that it was an issue with the default config of interactsh server affecting all the server running self-hosted instance of interactsh, as a result - cname entry has been removed in the latest release.

#### Impact
This allows one to host / run arbitrary client side code (XSS) in a user's browser when browsing the vulnerable subdomain, for more details on the impact, please read this [detailed blogpost](https://labs.detectify.com/2014/10/21/hostile-subdomain-takeover-using-herokugithubdesk-more/) from Detectify.
#### Patches
Update to [Interactsh server v1.0.0 ](https://github.com/projectdiscovery/interactsh/releases/tag/v1.0.0)with `go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-server@latest`

#### References
https://github.com/projectdiscovery/interactsh/issues/136

#### For more information
If you have any questions or comments about this advisory:
* Email us at [security@projectdiscovery.io](mailto:security@projectdiscovery.io)

## References
- https://github.com/projectdiscovery/interactsh/security/advisories/GHSA-m36x-mgfh-8g78
- https://nvd.nist.gov/vuln/detail/CVE-2023-36474
- https://github.com/projectdiscovery/interactsh/issues/136
- https://github.com/projectdiscovery/interactsh/pull/155
- https://github.com/projectdiscovery/interactsh
- https://labs.detectify.com/2014/10/21/hostile-subdomain-takeover-using-herokugithubdesk-more
