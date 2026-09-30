# [H] CVE-2016-5385

## Summary
Severity: High
Advisory: CVE-2016-5385
Aliases: GHSA-m6ch-gg5f-wxx3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-19
Source: https://osv.dev/vulnerability/CVE-2016-5385
Type: osv

## Details
PHP through 7.0.8 does not attempt to address RFC 3875 section 4.1.18 namespace conflicts and therefore does not protect applications from the presence of untrusted client data in the HTTP_PROXY environment variable, which might allow remote attackers to redirect an application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, as demonstrated by (1) an application that makes a getenv('HTTP_PROXY') call or (2) a CGI configuration of PHP, aka an "httpoxy" issue.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7RMYXAVNYL2MOBJTFATE73TOVOEZYC5R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GXFEIMZPSVGZQQAYIQ7U7DFVX3IBSDLF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KZOIUYZDBWNDDHC6XTOLZYRMRXZWTJCP/
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00003.html
- http://rhn.redhat.com/errata/RHSA-2016-1609.html
- http://rhn.redhat.com/errata/RHSA-2016-1610.html
- http://rhn.redhat.com/errata/RHSA-2016-1611.html
- http://rhn.redhat.com/errata/RHSA-2016-1612.html
- http://rhn.redhat.com/errata/RHSA-2016-1613.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.kb.cert.org/vuls/id/797896
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91821
- http://www.securitytracker.com/id/1036335
- https://github.com/guzzle/guzzle/releases/tag/6.2.1
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03770en_us
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05320149
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05333297
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- https://httpoxy.org/
