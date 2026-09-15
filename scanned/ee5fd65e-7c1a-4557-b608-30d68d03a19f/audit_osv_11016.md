# [C] CVE-2017-5638

## Summary
Severity: Critical
Advisory: CVE-2017-5638
Aliases: GHSA-j77q-2qqg-6989
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-11
Source: https://osv.dev/vulnerability/CVE-2017-5638
Type: osv

## Details
The Jakarta Multipart parser in Apache Struts 2 2.3.x before 2.3.32 and 2.5.x before 2.5.10.1 has incorrect exception handling and error-message generation during file-upload attempts, which allows remote attackers to execute arbitrary commands via a crafted Content-Type, Content-Disposition, or Content-Length HTTP header, as exploited in the wild in March 2017 with a Content-Type header containing a #cmd= string.

## References
- https://git1-us-west.apache.org/repos/asf?p=struts.git%3Ba=commit%3Bh=352306493971e7d5a756d61780d57a76eb1f519a
- https://git1-us-west.apache.org/repos/asf?p=struts.git%3Ba=commit%3Bh=6b8272ce47160036ed120a48345d9aa884477228
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03733en_us
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2017-5638
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2017-002.txt
- http://www.eweek.com/security/apache-struts-vulnerability-under-attack.html
- http://www.securityfocus.com/bid/96729
- http://www.securitytracker.com/id/1037973
- https://cwiki.apache.org/confluence/display/WW/S2-045
- https://cwiki.apache.org/confluence/display/WW/S2-046
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03749en_us
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03723en_us
- https://security.netapp.com/advisory/ntap-20170310-0001/
- https://struts.apache.org/docs/s2-045.html
- https://struts.apache.org/docs/s2-046.html
- https://support.lenovo.com/us/en/product_security/len-14200
- https://twitter.com/theog150/status/841146956135124993
- https://www.imperva.com/blog/2017/03/cve-2017-5638-new-remote-code-execution-rce-vulnerability-in-apache-struts-2/
- https://www.kb.cert.org/vuls/id/834067
- https://www.symantec.com/security-center/network-protection-security-advisories/SA145
