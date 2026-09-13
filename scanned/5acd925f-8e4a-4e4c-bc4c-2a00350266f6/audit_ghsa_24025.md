# [C] XML External Entity Reference in weixin-java-tools

## Summary
Severity: Critical
Advisory: GHSA-h755-h99p-9ffv
CVE: CVE-2019-5312
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h755-h99p-9ffv
Type: github-advisory

## Affected
- Maven: `com.github.binarywang:weixin-java-common` — affected >=0 <3.3.2.B

## Details
An issue was discovered in weixin-java-tools. There is an XXE vulnerability in the getXmlDoc method of the BaseWxPayResult.java file. NOTE: this issue exists because of an incomplete fix for CVE-2018-20318.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5312
- https://github.com/Wechat-Group/WxJava/issues/903
- https://github.com/Wechat-Group/WxJava/issues/903#issuecomment-453747039
- https://github.com/Wechat-Group/WxJava/commit/8ec61d1328f50e23cd14285a950ca57a088b32b2
