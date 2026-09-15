# [M] Grafana directory traversal for .cvs files

## Summary
Severity: Medium
Advisory: GHSA-7533-c8qv-jm9m
CVE: CVE-2021-43815
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-7533-c8qv-jm9m
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=8.0.0-beta3 <8.3.2

## Details
Today we are releasing Grafana `8.3.2` and `7.5.12`. This patch release includes a moderate severity security fix for directory traversal for arbitrary `.csv` files. It only affects instances that have the developer testing tool called [TestData DB data source](https://grafana.com/docs/grafana/latest/datasources/testdata/) enabled and configured.

The vulnerability is limited in scope, and only allows access to files with the extension `.csv` to **authenticated users only.**

This is a follow-up patch release to our recent [CVE-2021-43798](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-43798) release. If you haven’t read about that high severity security fix, we recommend that you review the [initial blog post](https://grafana.com/blog/2021/12/07/grafana-8.3.1-8.2.7-8.1.8-and-8.0.7-released-with-high-severity-security-fix/), along with our [update on the 0day](https://grafana.com/blog/2021/12/08/an-update-on-0day-cve-2021-43798-grafana-directory-traversal/).

Given the attention CVE-2021-43798 has brought, there’s a risk that additional researchers will find CVE-2021-43813. Out of an abundance of caution and given that both CVE-2021-43813 and CVE-2021-pending are only CVSS Score 4.3 Moderate CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N through their limited scope we are immediately releasing to the public, and on a Friday.

We identified several vulnerability issues in the last few weeks, and at a higher rate than in the years before. The infosec industry usually comes together after a few CVEs and we benefit from that extra scrutiny. Although it can be difficult, ultimately it's for the overall benefit of Grafana and the community. Please know that this is a top priority for us. We are spending significant resources on this in the remainder of 2021 already, including full outside assessment. We will continue and increase this investment in 2022 and beyond.

Release 8.3.2, only containing security fixes:

- [Download Grafana 8.3.2](https://grafana.com/grafana/download/8.3.2)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-8-3-2/)

Release 7.5.12, only containing security fixes:

- [Download Grafana 7.5.12](https://grafana.com/grafana/download/7.5.12)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-7-5-12/)

## Directory Traversal [CVE-2021-43815](https://github.com/grafana/grafana/security/advisories/GHSA-7533-c8qv-jm9m)


### Summary 

CVSS Score: 4.3 Moderate CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N

On 2021-12-09, GitHub Security Labs notified us of a vulnerability through which authenticated users could read out fully lowercase or fully uppercase `.md` files through directory traversal. Doing our own follow-up investigation we found a related vulnerability through which authenticated users could read out arbitrary `.csv` files through directory traversal. Thanks to our defense-in-depth approach, at no time has [Grafana Cloud](https://grafana.com/cloud) been vulnerable.

**The vulnerable URL path is**: `/api/ds/query`

### Affected versions with moderate severity 

CVE-2021-43815: Grafana 8.0.0-beta3 - 8.3.1

### Solutions and mitigations

All installations between 5.0.0 and 8.3.1 should be upgraded as soon as possible.

If you can not upgrade, running a reverse proxy in front of Grafana that normalizes the PATH of the request will mitigate the vulnerability. The proxy will have to also be able to handle url encoded paths. 

Thanks to our defense-in-depth approach, [Grafana Cloud](https://grafana.com/cloud) instances have not been affected by the vulnerability.

### Timeline and postmortem

Here is a detailed timeline starting from when we originally learned of the issue. All times in UTC.

* 2021-12-09 16:07: As part of investigation of the [CVE-2021-43813](https://github.com/grafana/grafana/security/advisories/GHSA-c3q8-26ph-9g2q) we have discovered that .csv files are affected and can be read out via /api/ds/query
* 2021-12-09 16:10: PR with a possible fix the markdown path traversal is raised in private mirror repo
* 2021-12-09 19:05: Fix confirmed
* 2021-12-09 23:00: Decision release to direct to public on 2021-12-10 14:30 UTC
* 2021-12-09 23:36: Announcement email sent to customers
* 2021-12-10 10:11: Decision to split out `.csv` vulnerability into its own CVE


### Acknowledgement

We would like to thank the [GitHub Security Lab team](https://securitylab.github.com/) for responsibly disclosing CVE-2021-43813 to us.

## Reporting security Issues

If you think you have found a security vulnerability, please send a report to [security@grafana.com](mailto:security@grafana.com). This address can be used for all of
Grafana Labs' open source and commercial products (including but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E  5CAA D125 8932 BE24 C5CA

The key is available from [keyserver.ubuntu.com](https://keyserver.ubuntu.com/pks/lookup?search=0xF9887BEA027A049FAE8E5CAAD1258932BE24C5CA&fingerprint=on&op=index).

## Security announcements

We maintain a [security category on our blog](https://grafana.com/tags/security/), where we will always post a summary, remediation, and mitigation details for any patch containing security fixes. 

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-7533-c8qv-jm9m
- https://nvd.nist.gov/vuln/detail/CVE-2021-43815
- https://github.com/grafana/grafana/commit/d6ec6f8ad28f0212e584406730f939105ff6c6d3
- https://github.com/grafana/grafana/commit/fd48aee61e4328aae8d5303a9efd045fa0ca308d
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v8.3.2
- https://grafana.com/blog/2021/12/10/grafana-8.3.2-and-7.5.12-released-with-moderate-severity-security-fix
- https://security.netapp.com/advisory/ntap-20220107-0006
- http://www.openwall.com/lists/oss-security/2021/12/10/4
