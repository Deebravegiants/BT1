# [M] Cross-site Scripting in video.js

## Summary
Severity: Medium
Advisory: GHSA-pp7m-6j83-m7r6
CVE: CVE-2021-23414
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-10
Source: https://github.com/advisories/GHSA-pp7m-6j83-m7r6
Type: github-advisory

## Affected
- npm: `video.js` — affected >=0 <7.14.3

## Details
This affects the package video.js before 7.14.3.
 The src attribute of track tag allows to bypass HTML escaping and execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23414
- https://github.com/videojs/video.js/commit/b3acf663641fca0f7a966525a72845af7ec5fab2
- https://github.com/videojs/video.js
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DHYIIAUXUBHMBEDYU7TYNZXEN2W2SA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/74SXNGA5RIWM7QNX7H3G7SYIQLP4UUGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NLRJB5JNKK3VVBLV3NH3RI7COEDAXSAB
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1533588
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1533587
- https://snyk.io/vuln/SNYK-JS-VIDEOJS-1533429
