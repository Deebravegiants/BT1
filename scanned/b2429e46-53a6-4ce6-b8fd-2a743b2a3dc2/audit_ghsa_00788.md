# [M] Cross-Site Scripting in @novnc/novnc

## Summary
Severity: Medium
Advisory: GHSA-49rv-g7w5-m8xx
CVE: CVE-2017-18635
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-08-28
Source: https://github.com/advisories/GHSA-49rv-g7w5-m8xx
Type: github-advisory

## Affected
- npm: `@novnc/novnc` — affected >=0 <0.6.2

## Details
Versions of `@novnc/novnc` prior to 0.6.2 are vulnerable to Cross-Site Scripting (XSS). The package fails to validate input from the remote VNC server such as the VNC server name. This allows an attacker in control of the remote server to execute arbitrary JavaScript in the noVNC web page. It affects any users of `include/ui.js` and users of `vnc_auto.html` and `vnc.html`.


## Recommendation

Upgrade to version 0.6.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18635
- https://github.com/novnc/noVNC/issues/748
- https://github.com/novnc/noVNC/commit/6048299a138e078aed210f163111698c8c526a13#diff-286f7dc7b881e942e97cd50c10898f03L534
- https://access.redhat.com/errata/RHSA-2020:0754
- https://bugs.launchpad.net/horizon/+bug/1656435
- https://github.com/ShielderSec/cve-2017-18635
- https://github.com/novnc/noVNC
- https://github.com/novnc/noVNC/releases/tag/v0.6.2
- https://lists.debian.org/debian-lts-announce/2019/10/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00024.html
- https://snyk.io/vuln/SNYK-JS-NOVNCNOVNC-469136
- https://usn.ubuntu.com/4522-1
- https://www.npmjs.com/advisories/1204
- https://www.shielder.it/blog/exploiting-an-old-novnc-xss-cve-2017-18635-in-openstack
