# [M] CVE-2016-1000109

## Summary
Severity: Medium
Advisory: CVE-2016-1000109
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2016-1000109
Type: osv

## Details
HHVM does not attempt to address RFC 3875 section 4.1.18 namespace conflicts and therefore does not protect CGI applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect a CGI application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an "httpoxy" issue. This issue affects HHVM versions prior to 3.9.6, all versions between 3.10.0 and 3.12.4 (inclusive), and all versions between 3.13.0 and 3.14.2 (inclusive).

## References
- https://www.facebook.com/security/advisories/cve-2016-1000109
- https://github.com/facebook/hhvm/commit/423b4b719afd5ef4e6e19d8447fbf7b6bc0d0a25
- https://httpoxy.org/
