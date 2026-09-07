# [M] Arbitrary Code Injection in mobile-icon-resizer

## Summary
Severity: Medium
Advisory: GHSA-mxjr-xmcg-fg7w
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-27
Source: https://github.com/advisories/GHSA-mxjr-xmcg-fg7w
Type: github-advisory

## Affected
- npm: `mobile-icon-resizer` — affected >=0.2.0 <0.4.3

## Details
mobile-icon-resizer resizes large images for use as icons for iOS and Android.

mobile-icon-resizer has a code execution vulnerability in versions before 0.4.3.

mobile-icon-resizer takes an options object as an argument to define the resulting icons as such:
```
var options = {
  config: './config.js'
}
resize(options, function(err){});
```
config.js would need to be a file on the filesystem and look something like:
```
var config = {
  iOS: {
    "images": [
     /* iOS image definitions are not vulnerable */
    ]
  },
  android: {
    "images" : [
      {
        "baseRatio" : "console.log('Executing script as baseRatio property')",
        "folder" : "drawable-ldpi"
      },
      {
        "ratio" : "console.log('Executing script as ratio property')",
        "folder" : "drawable-mdpi"
      },
    /* other android image defintiions ... */
    ]
  }
};

exports = module.exports = config;
```
The parameters `ratio` and `baseRatio` are passed directly to `eval()`, thus allowing dynamic javascript payloads to be executed.


## Recommendation

Update to version 0.4.3 or later.

## References
- https://github.com/muzzley/mobile-icon-resizer/issues/8
- https://github.com/muzzley/mobile-icon-resizer/commit/a6c50f884bd282d74ab77e1fce6317d5d0dd2f0f
- https://snyk.io/vuln/npm:mobile-icon-resizer:20160408
- https://www.npmjs.com/advisories/317
