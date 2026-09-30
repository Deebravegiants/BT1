# [M] CVE-2016-1000107

## Summary
Severity: Medium
Advisory: CVE-2016-1000107
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/CVE-2016-1000107
Type: osv

## Details
inets in Erlang possibly 22.1 and earlier follows RFC 3875 section 4.1.18 and therefore does not protect applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect an application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an "httpoxy" issue.

## References
- http://www.openwall.com/lists/oss-security/2016/07/18/6
- https://httpoxy.org/
- https://security-tracker.debian.org/tracker/CVE-2016-1000107
- https://bugs.erlang.org/browse/ERL-198
