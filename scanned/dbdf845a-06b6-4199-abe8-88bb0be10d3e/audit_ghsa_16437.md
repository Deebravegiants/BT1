# [M] Grafana Cross Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-cmf4-h3xc-jw8w
CVE: CVE-2022-21703
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-cmf4-h3xc-jw8w
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana/pkg/web` — affected >=3.0-beta1 <7.5.15
- Go: `github.com/grafana/grafana/pkg/web` — affected >=8.0.0 <8.3.5

## Details
Today we are releasing Grafana 8.3.5 and 7.5.15. This patch release includes MEDIUM severity security fix for Cross Site Request Forgery for Grafana.

Release v.8.3.5, only containing security fixes:

- [Download Grafana 8.3.5](https://grafana.com/grafana/download/8.3.5)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-8-3-5/)

Release v.7.5.15, only containing security fixes:

- [Download Grafana 7.5.15](https://grafana.com/grafana/download/7.5.15)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-7-5-15/)

## CSRF ([CVE-2022-21703](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-21703))

### Summary
On Jan. 18, security researchers [jub0bs](https://twitter.com/jub0bs) and [abrahack](https://twitter.com/theabrahack) contacted Grafana to disclose a CSRF vulnerability which allows anonymous attackers to elevate their privileges by mounting cross-origin attacks against authenticated high-privilege Grafana users (for example, Editors or Admins). 

We believe that this vulnerability is rated at CVSS 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N). 

### Impact
An attacker can exploit this vulnerability for privilege escalation by tricking an authenticated user into inviting the attacker as a new user with high privileges. 

### Affected versions with MEDIUM severity 
All Grafana >=3.0-beta1 versions are affected by this vulnerability.

### Solutions and mitigations

All installations after Grafana v3.0-beta1 should be upgraded as soon as possible.

Note that if you are running Grafana behind any reverse proxy, you need to make sure that you are passing the original Host and Origin headers from the client request to Grafana.

In the case of Apache Server, you need to add `ProxyPreserveHost on` in your proxy [configuration](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html). In case of NGINX, you can need to add `proxy_set_header Host $http_host;` in your [configuration](http://nginx.org/en/docs/http/ngx_http_proxy_module.html).

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana.

### Timeline and postmortem

Here is a detailed timeline starting from when we originally learned of the issue. All times in UTC.
- 2022-01-18 03:00 Issue submitted by external researchers
- 2022-01-18 17:25 Vulnerability confirmed reproducible 
- 2022-01-19 07:40 CVSS score confirmed 6.8 at maximum and MEDIUM impact
- 2022-01-19 07:40 Begin mitigation for Grafana Cloud
- 2022-01-19 17:00 CVE requested 
- 2022-01-19 19:50 GitHub issues CVE-2022-21703
- 2022-01-21 10:50 PR with fix opened
- 2022-01-21 14:13 Private release planned for 2022-01-25, and public release planned for 2022-02-01.
- 2022-01-25 12:00 Private release
- 2022-02-01 12:00 During the public release process, we realized that private 7.x release was incomplete. Abort public release, send second private release to customers using 7.x
- 2022-02-08 12:00 Public release

### Acknowledgement

We would like to thank [jub0bs](https://twitter.com/jub0bs) and [abrahack](https://twitter.com/theabrahack) for responsibly disclosing the vulnerability.

### Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

### Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-cmf4-h3xc-jw8w
- https://nvd.nist.gov/vuln/detail/CVE-2022-21703
- https://github.com/grafana/grafana/pull/45083
- https://grafana.com/blog/2022/02/08/grafana-7.5.15-and-8.3.5-released-with-moderate-severity-security-fixes
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2PFW6Q2LXXWTFRTMTRN4ZGADFRQPKJ3D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/36GUEPA5TPSC57DZTPYPBL6T7UPQ2FRH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HLAQRRGNSO5MYCPAXGPH2OCSHOGHSQMQ
- https://security.netapp.com/advisory/ntap-20220303-0005
