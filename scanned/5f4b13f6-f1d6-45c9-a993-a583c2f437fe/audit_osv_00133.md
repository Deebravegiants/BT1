# [H] ALPINE-CVE-2016-5387

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5387
Ecosystem: Alpine:v3.4
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5387
Type: osv

## Affected
- Alpine:v3.4: `apache2` — affected >=0 <2.4.23-r1

## Details
The Apache HTTP Server through 2.4.23 follows RFC 3875 section 4.1.18 and therefore does not protect applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect an application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an "httpoxy" issue.  NOTE: the vendor states "This mitigation has been assigned the identifier CVE-2016-5387"; in other words, this is not a CVE ID for a vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5387
