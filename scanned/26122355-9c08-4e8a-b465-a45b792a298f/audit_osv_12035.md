# [H] CVE-2018-1000817

## Summary
Severity: High
Advisory: CVE-2018-1000817
Aliases: GHSA-w73q-mc9g-j56x
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000817
Type: osv

## Details
Asset Pipeline Grails Plugin Asset-pipeline plugin version Prior to 2.14.1.1, 2.15.1 and 3.0.6 contains a Incorrect Access Control vulnerability in Applications deployed in Jetty that can result in Download .class files and any arbitrary file. This attack appear to be exploitable via Specially crafted GET request containing directory traversal from assets-pipeline context. This vulnerability appears to have been fixed in 2.14.1.1 (for Grails 2.x), 2.15.1 (for Grails 3 and Java 7) and 3.0.6 (for Grails 3 and Java 8).

## References
- https://github.com/grails/grails-core/issues/11068
- http://grailsblog.objectcomputing.com/posts/2018/09/23/security-vulnerability-in-asset-pipeline-and-jetty.html
