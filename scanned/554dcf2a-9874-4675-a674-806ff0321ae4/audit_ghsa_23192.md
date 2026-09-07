# [M] Silverstripe CMS Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-fh35-p8ph-p545
CVE: CVE-2015-5062
CWE: CWE-601
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fh35-p8ph-p545
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0
- Packagist: `silverstripe/framework` — affected >=0

## Details
Open redirect vulnerability in SilverStripe CMS & Framework 3.1.13 allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a URL in the returnURL parameter to dev/build.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5062
- https://web.archive.org/web/20200228091958/http://www.securityfocus.com/bid/75419
- https://web.archive.org/web/20201209000421/http://www.securityfocus.com/archive/1/535716/100/0/threaded
- http://hyp3rlinx.altervista.org/advisories/AS-SILVERSTRIPE0607.txt
- http://packetstormsecurity.com/files/132223/SilverStripe-CMS-3.1.13-XSS-Open-Redirect.html
