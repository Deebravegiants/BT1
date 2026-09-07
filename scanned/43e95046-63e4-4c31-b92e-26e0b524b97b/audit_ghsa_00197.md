# [M] Cross-Site Scripting in i18next

## Summary
Severity: Medium
Advisory: GHSA-cmh5-qc8w-xvcq
CVE: CVE-2017-16010
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-cmh5-qc8w-xvcq
Type: github-advisory

## Affected
- npm: `i18next` — affected >=2.0.0 <3.4.4

## Details
Affected versions of `i18next` may fail to sanitize user input when certain configuration options are used. When using the `.init` method, passing interpolation options without passing an `escapeValue` will default to `undefined` rather than the assumed `true`. 

## Proof of Concept

```js
var init = i18n.init({
  interpolation: {
    prefix: "__",
    suffix: "__",
    escapeValue: true
  }
}, function(){
  var test = i18n.t('__firstName__ __lastName__', {
        firstName: 'Bob',
        lastName: '["foo","bar"]',
  });
  console.log(test);
});
```
When `escapeValue` is explicitly passed, the result of `test` is: 

```html
&lt;script&gt;alert(1)&lt;&#x2F;script&gt; Johnson
```

This is supposed to be the default. However, if `escapeValue` is not included, the result is the unescaped string: 
 
```html
<script>alert(1)</script> Johnson
```


## Recommendation

Update to version 3.4.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16010
- https://github.com/i18next/i18next/pull/826
- https://github.com/advisories/GHSA-cmh5-qc8w-xvcq
- https://www.npmjs.com/advisories/326
