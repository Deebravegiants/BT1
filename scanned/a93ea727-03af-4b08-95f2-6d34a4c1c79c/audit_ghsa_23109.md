# [M] Dojo Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mmjh-45vj-hfvf
CVE: CVE-2010-2274
CWE: CWE-601
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mmjh-45vj-hfvf
Type: github-advisory

## Affected
- Maven: `org.dojotoolkit:dojo` — affected >=1.0.0 <1.0.3
- Maven: `org.dojotoolkit:dojo` — affected >=1.1.0 <1.1.2
- Maven: `org.dojotoolkit:dojo` — affected >=1.2.0 <1.2.4
- Maven: `org.dojotoolkit:dojo` — affected >=1.3.0 <1.3.3
- Maven: `org.dojotoolkit:dojo` — affected >=1.4.0 <1.4.2

## Details
Multiple open redirect vulnerabilities in Dojo 1.0.x before 1.0.3, 1.1.x before 1.1.2, 1.2.x before 1.2.4, 1.3.x before 1.3.3, and 1.4.x before 1.4.2 allow remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via unspecified vectors, possibly related to dojo/resources/iframe_history.html, dojox/av/FLAudio.js, dojox/av/FLVideo.js, dojox/av/resources/audio.swf, dojox/av/resources/video.swf, util/buildscripts/jslib/build.js, util/buildscripts/jslib/buildUtil.js, and util/doh/runner.html.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2274
- https://github.com/cometd/dojo-maven
- https://web.archive.org/web/20100617172214/http://secunia.com/advisories/40007
- https://web.archive.org/web/20100629020444/http://secunia.com/advisories/38964
- http://dojotoolkit.org/blog/post/dylan/2010/03/dojo-security-advisory
- http://www-01.ibm.com/support/docview.wss?uid=swg21431472
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50833
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50849
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50856
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50896
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50932
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50958
- http://www-1.ibm.com/support/docview.wss?uid=swg1LO50994
