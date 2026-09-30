# [M] CVE-2020-7642

## Summary
Severity: Medium
Advisory: CVE-2020-7642
Aliases: GHSA-hg2p-2cvq-4ppv, SNYK-JS-LAZYSIZES-567144
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-04-22
Source: https://osv.dev/vulnerability/CVE-2020-7642
Type: osv

## Details
lazysizes through 5.2.0 allows execution of malicious JavaScript. The following attributes are not sanitized by the video-embed plugin: data-vimeo, data-vimeoparams, data-youtube and data-ytparams which can be abused to inject malicious JavaScript.

## References
- https://github.com/aFarkas/lazysizes/commit/3720ab8262552d4e063a38d8492f9490a231fd48
- https://snyk.io/vuln/SNYK-JS-LAZYSIZES-567144
