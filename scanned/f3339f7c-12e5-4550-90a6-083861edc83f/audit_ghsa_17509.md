# [M] File Browser allows sensitive data to be transferred in URL

## Summary
Severity: Medium
Advisory: GHSA-rmwh-g367-mj4x
CVE: CVE-2025-52901
CWE: CWE-598
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-rmwh-g367-mj4x
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.33.9
- Go: `github.com/filebrowser/filebrowser` — affected >=0

## Details
## Summary

URLs that are accessed by a user are commonly logged in many locations, both server- and client-side. It is thus good practice to never transmit any secret information as part of a URL. The *Filebrowser* violates this practice, since access tokens are used as GET parameters.

## Impact

The *JSON Web Token (JWT)* which is used as a session identifier will get leaked to anyone having access to the URLs accessed by the user. This will give the attacker full access to the user's account and, in consequence, to all sensitive files the user has access to.

## Description

Sensitive information in URLs is logged by several components (see the following examples), even if access is protected by TLS.

* The browser history
* The access logs on the affected web server
* Proxy servers or reverse proxy servers
* Third-party servers via the HTTP referrer header

In case attackers can access certain logs, they could read the included sensitive data.

## Proof of Concept ##

When a file is downloaded via the web interface, the JWT is part of the URL:

```http
GET /api/raw/testdir/testfile.txt?auth=eyJh[...]_r4EQ HTTP/1.1
Host: filebrowser.local:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Referer: http://filebrowser.local:8080/files/testdir/
Cookie: auth=eyJh[...]_r4EQ
Upgrade-Insecure-Requests: 1
Priority: u=0, i
```

This also happens when a new *command session* is started:

```http
GET /api/command/?auth=eyJh[...]YW8BA HTTP/1.1
Host: filebrowser.local:8080
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Sec-WebSocket-Version: 13
Origin: http://filebrowser.local:8080
Sec-WebSocket-Key: oqQMrF7R34D3lAkj1+ZHTw==
Connection: keep-alive, Upgrade
Cookie: auth=eyJh[...]YW8BA
Pragma: no-cache
Cache-Control: no-cache
Upgrade: websocket
```

## Recommended Countermeasures ##

Sensitive data like session tokens or user credentials should be transmitted via HTTP headers or the HTTP body only, never in the URL.

## Timeline ##

* `2025-03-27` Identified the vulnerability in version 2.32.0
* `2025-04-11` Contacted the project
* `2025-04-29` Vulnerability disclosed to the project
* `2025-06-25` Uploaded advisories to the project's GitHub repository
* `2025-06-26` CVE ID assigned by GitHub
* `2025-06-26` Fix released in version 2.33.9

## References ##

* [CWE-598: Use of GET Request Method With Sensitive Query Strings](https://cwe.mitre.org/data/definitions/598.html)
* [Original Advisory](https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250327-03_Filebrowser_Sensitive_Data_Transferred_In_URL)

## Credits ##

* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-rmwh-g367-mj4x
- https://nvd.nist.gov/vuln/detail/CVE-2025-52901
- https://github.com/filebrowser/filebrowser/commit/d5b39a14fd3fc0d1c364116b41289484df7c27b2
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.33.9
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250327-03_Filebrowser_Sensitive_Data_Transferred_In_URL
- https://pkg.go.dev/vuln/GO-2025-3794
