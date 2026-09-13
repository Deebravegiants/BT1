# [M] CVE-2016-1000108

## Summary
Severity: Medium
Advisory: CVE-2016-1000108
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/CVE-2016-1000108
Type: osv

## Details
yaws before 2.0.4 does not attempt to address RFC 3875 section 4.1.18 namespace conflicts and therefore does not protect CGI applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect a CGI application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an "httpoxy" issue.

## References
- http://www.openwall.com/lists/oss-security/2016/07/18/6
- https://raw.githubusercontent.com/distributedweaknessfiling/cvelist/master/2016/1000xxx/CVE-2016-1000108.json
- https://security-tracker.debian.org/tracker/CVE-2016-1000108
- https://github.com/klacke/yaws/commit/9d8fb070e782c95821c90d0ca7372fc6d7316c78#diff-54053c47eb173a90c26ed19bd9d106c1
