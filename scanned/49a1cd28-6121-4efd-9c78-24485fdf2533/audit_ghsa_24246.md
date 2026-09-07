# [M] QooxDoo XSS in Callback Parameter

## Summary
Severity: Medium
Advisory: GHSA-pchf-755w-jj6v
CVE: CVE-2011-1714
CWE: CWE-79
Ecosystem: npm
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pchf-755w-jj6v
Type: github-advisory

## Affected
- npm: `qooxdoo` — affected >=0

## Details
Cross-site scripting (XSS) vulnerability in `framework/source/resource/qx/test/jsonp_primitive.php` in QooxDoo 1.3 and possibly other versions, as used in eyeOS 2.2 and 2.3, and possibly other products allows remote attackers to inject arbitrary web script or HTML via the callback parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1714
- https://exchange.xforce.ibmcloud.com/vulnerabilities/66574
- https://web.archive.org/web/20110410180449/http://blog.eyeos.org/en/2011/04/07/about-some-eyeos-security-issues
- https://web.archive.org/web/20201207203617/http://www.autosectools.com/Advisories/eyeOS.2.3_Reflected.Cross-site.Scripting_172.html
- https://web.archive.org/web/20201207203620/http://www.securityfocus.com/bid/47184
- http://www.exploit-db.com/exploits/17127
