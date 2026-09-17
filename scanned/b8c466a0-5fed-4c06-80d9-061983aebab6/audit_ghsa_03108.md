# [C] Arbitrary Code Execution in underscore

## Summary
Severity: Critical
Advisory: GHSA-cf4h-3jhx-xvhq
CVE: CVE-2021-23358
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-cf4h-3jhx-xvhq
Type: github-advisory

## Affected
- npm: `underscore` — affected >=1.3.2 <1.12.1

## Details
The package `underscore` from 1.13.0-0 and before 1.13.0-2, from 1.3.2 and before 1.12.1 are vulnerable to Arbitrary Code Execution via the template function, particularly when a variable property is passed as an argument as it is not sanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23358
- https://github.com/jashkenas/underscore/pull/2917
- https://github.com/jashkenas/underscore/commit/4c73526d43838ad6ab43a6134728776632adeb66
- https://www.tenable.com/security/tns-2021-14
- https://www.npmjs.com/package/underscore
- https://www.debian.org/security/2021/dsa-4883
- https://snyk.io/vuln/SNYK-JS-UNDERSCORE-1080984
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1081503
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBJASHKENAS-1081505
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1081504
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://security.netapp.com/advisory/ntap-20240808-0003
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FGEE7U4Z655A2MK5EW4UQQZ7B64XJWBV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EOKATXXETD2PF3OR36Q5PD2VSVAR6J5Z
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGEE7U4Z655A2MK5EW4UQQZ7B64XJWBV
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EOKATXXETD2PF3OR36Q5PD2VSVAR6J5Z
- https://lists.debian.org/debian-lts-announce/2021/03/msg00038.html
- https://lists.apache.org/thread.html/re69ee408b3983b43e9c4a82a9a17cbbf8681bb91a4b61b46f365aeaf@%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/re69ee408b3983b43e9c4a82a9a17cbbf8681bb91a4b61b46f365aeaf%40%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/rbc84926bacd377503a3f5c37b923c1931f9d343754488d94e6f08039@%3Cissues.cordova.apache.org%3E
