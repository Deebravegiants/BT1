# [M] Grafana vulnerable to Stored Cross-site Scripting in Text plugin

## Summary
Severity: Medium
Advisory: GHSA-7rqg-hjwc-6mjf
CVE: CVE-2023-22462
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-7rqg-hjwc-6mjf
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.2.0 <9.2.10
- Go: `github.com/grafana/grafana` — affected >=9.3.0 <9.3.4

## Details
### Description 
On 2023-01-01 during an internal audit of Grafana, a member of the security team found a stored XSS vulnerability affecting the core plugin "Text".

The stored XSS vulnerability requires several user interactions in order to be fully exploited. The vulnerability was possible due to  React's render cycle that will pass though the unsanitized HTML code, but in the next cycle the HTML is cleaned up and saved in Grafana's database.

### Impact
An attacker needs to have the Editor role in order to change a Text panel to include JavaScript. later, an another user needs to edit the same Text panel, and click on "Markdown" or "HTML" for the code to be executed. This means that vertical privilege escalation is possible, where a user with Editor role can change to a known password for a user having Admin role if the user with Admin role executes malicious JavaScript viewing a dashboard.   

### Impacted versions
Grafana versions between 9.2.0 and 9.2.10. and between 9.3.0 and 9.3.4

### Solutions and mitigations
Update your Grafana instance.


## Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

## Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-7rqg-hjwc-6mjf
- https://nvd.nist.gov/vuln/detail/CVE-2023-22462
- https://github.com/grafana/grafana/commit/db83d5f398caffe35c5846cfa7727d1a2a414165
- https://github.com/grafana/grafana
- https://grafana.com/blog/2023/02/28/grafana-security-release-new-versions-with-security-fixes-for-cve-2023-0594-cve-2023-0507-and-cve-2023-22462
- https://security.netapp.com/advisory/ntap-20230413-0004
