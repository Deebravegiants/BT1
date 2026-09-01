# [C] Multiple HTTP Smuggling reports

## Summary
Severity: Critical (CVSS 9.8)
Program: Internet Bug Bounty
Weakness: HTTP Request Smuggling
Reporter: regilero
State: resolved
Disclosed: 2019-11-12T23:44:23.458Z
CVE: CVE-2017-7658, CVE-2018-8004, CVE-2017-7656, CVE-2017-7657, CVE-2016-8743, CVE-2015-3183, CVE-2016-10711, CVE-2016-2086, CVE-2016-2216, CVE-2016-6816, CVE-2015-8852, CVE-2015-5739, CVE-2015-5740
Source: https://hackerone.com/reports/648434

## Details
Theses reports spreads other several years and are all about **HTTP Smuggling issues**
(HTTP Requests or Responses splitting, Cache Poisoning, Security filter bypass).
I've made reports on a wide range of open source projects, explaining
the (not always easy) problems to the various security maintainers and testing the fixs.

The starting point for this work was the 2005 work published by Amit Klein and some others:

 * 2004 - Amit Klein : "Divide and Conquer: HTTP Response Splitting, Web Cache Poisoning Attacks, and Related Topics" https://packetstormsecurity.com/papers/general/whitepaper_httpresponse.pdf
 * 2005 - Chaim Linhart, Amit Klein, Ronen Heled, Steve Orrin: "HTTP Request Smuggling" https://www.cgisecurity.com/lib/HTTP-Request-Smuggling.pdf
 * 2006 - Amit Klein: "HTTP Message Splitting, Smuggling and Other Animals" www.owasp.org/images/1/1a/OWASPAppSecEU2006_HTTPMessageSplittingSmugglingEtc.ppt 
 * 2005 - Amit Klein: "HTTP Request Smuggling - ERRATA (the IIS 48K buffer phenomenon)" 
 * 2006 - Amit Klein: “HTTP Response Smuggling” https://www.securityfocus.com/archive/1/425593
 * 2006 - Amit Klein : HTTP Response Smuggling http://lists.webappsec.org/pipermail/websecurity_lists.webappsec.org/2006-February/000836.html
 * RFC 7230 section 9 (splitting, parsing, smuggling, poisoning) https://tools.ietf.org/html/rfc7230#section-9

And also the works of James Kettle on HTTP Host headers "Practical HTTP Host header attacks (Absolute uri in host headers)"
https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html
and, later, his work on ESI server or pingbacks and cache attacks or Pratical Web Cache Poisoning.

In 2015, Starting from these past studies, I studied **Apache**, **Nginx**, **Varnish** source code, I discovered
that a lot of smuggling problems were still present, found new ones based on overflows for the size
attributes (previous works were mostly based on doubling length information) and expanded my works on
**Golang**, **Nodejs**, **pound**, **HaProxy**, **Jetty**, **Tomcat**, **Apache Traffic Server**...

I sometime had to push for disclosure of fixed vulnerabilitie (Varnish 3) via bugtraq.
But in most of the case it's been a matter a patience -- the long time between reports and fixes
ha also something to deal with lazyness on my side as security is not the biggest part of my job --
as most of the fix implies updates on HTTP servers, which is not something as fast as updating a web
application framework. I did not get a security report or a CVE for each reported flaw, especially
on the first years. Smuggling is sometimes hard to explain (and public disclosure policies
are not always liked on HTTP servers dev teams).

The main problem of HTTP smuggling issues is that the final exploitation comes from **interactions between different http parsers**. If two actors badly interprets the HTTP message or disagree on the right
interpretation then bad things could happen. From the security maintainer point of view it's sometimes
easy to reject the problem as coming from the others.

It's also **very important** to understand that the attacker controls the HTTP message, **we do not use HTTP messages from browsers**, the attacker injects bad HTTP messages onto servers infrastructures, effects on the users comes later, when the real user HTTP messages reach the *infected* or  *shaken* servers. *Like when you do report a smuggling issue on hackerone reports, they prevent reporters that issues about header injection are not always security issues because we cannot control the user headers. That's a huge misunderstanding of smuggling payloads*.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/648434_
