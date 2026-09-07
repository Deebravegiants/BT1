# [M] Cross-Site Scripting in yui

## Summary
Severity: Medium
Advisory: GHSA-mj87-8xf8-fp4w
CVE: CVE-2013-4939
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-mj87-8xf8-fp4w
Type: github-advisory

## Affected
- npm: `yui` — affected >=0 <3.10.3

## Details
Affected versions of `yui` are vulnerable to cross-site scripting in the `uploader.swf` and `io.swf` utilities, via script injection in the url.



## Recommendation

YUI has published their recommendation to fix this issue. 
Their recommendation is to:
 - Delete self-hosted copies of these files if you are not using them
 - Use the Yahoo! CDN hosted files
 - Use the patched files provided on the YUI Library [here](https://yuilibrary.com/support/20130515-vulnerability/#resolution).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4939
- https://lists.apache.org/thread.html/72837f969cdf9b63a7e7337edd069fa3b3950eea7c997cc2ff61aa0c@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/d8b9403dbab85a51255614949938b619bd03b1c944c76c48c6996a0e@%3Cdev.zookeeper.apache.org%3E
- https://moodle.org/mod/forum/discuss.php?d=232496
- https://www.npmjs.com/advisories/332
- https://yuilibrary.com/support/20130515-vulnerability
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-39678
- http://yuilibrary.com/support/20130515-vulnerability
