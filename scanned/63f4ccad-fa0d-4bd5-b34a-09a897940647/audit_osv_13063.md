# [C] CVE-2018-17198

## Summary
Severity: Critical
Advisory: CVE-2018-17198
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2018-17198
Type: osv

## Details
Server-side Request Forgery (SSRF) and File Enumeration vulnerability in Apache Roller 5.2.1, 5.2.0 and earlier unsupported versions relies on Java SAX Parser to implement its XML-RPC interface and by default that parser supports external entities in XML DOCTYPE, which opens Roller up to SSRF / File Enumeration vulnerability. Note that this vulnerability exists even if Roller XML-RPC interface is disable via the Roller web admin UI. Mitigation: There are a couple of ways you can fix this vulnerability: 1) Upgrade to the latest version of Roller, which is now 5.2.2 2) Or, edit the Roller web.xml file and comment out the XML-RPC Servlet mapping as shown below: <!-- <servlet-mapping> <servlet-name>XmlRpcServlet</servlet-name> <url-pattern>/roller-services/xmlrpc</url-pattern> </servlet-mapping> -->

## References
- https://lists.apache.org/thread.html/94a36ed9c6241558b1c6181d8dd4ff263be7903abd1d20067d4330d5%40%3Cdev.roller.apache.org%3E
- http://www.securityfocus.com/bid/108496
