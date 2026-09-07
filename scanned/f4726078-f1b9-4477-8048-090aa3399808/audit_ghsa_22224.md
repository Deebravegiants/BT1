# [M] statics-server Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-393x-fr59-r8fg
CVE: CVE-2018-3771
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-393x-fr59-r8fg
Type: github-advisory

## Affected
- npm: `statics-server` — affected >=0

## Details
An XSS in statics-server <= 0.0.9 can be used via injected iframe in the filename when statics-server displays directory index in the browser. Statics-server does not implement any HTML escaping when displays directory index in the browser. Variable `v` is used in `<a href>` element without escaping, which allows to embed HTML `<iframe>` tag with `src` attribute points to another HTML file in the directory. This file can contain malicious JavaScript code, which will be executed:

```js
// ./node_modules/statics-server/index.js, line 18:

    if(fs.lstatSync(staticPath).isDirectory()){
        var files=fs.readdirSync(staticPath);
        var lis='';
        files.forEach((v,i)=>{
            if(fs.lstatSync(path.resolve(staticPath,v)).isDirectory()){
                lis+=`<li><a href="${req.url}${v}/">${v}/</a></li>`;
            }else {
                lis+=`<li><a href="${req.url}${v}">${v}</a></li>`
            }
        });

        (...)
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3771
- https://hackerone.com/reports/355458
