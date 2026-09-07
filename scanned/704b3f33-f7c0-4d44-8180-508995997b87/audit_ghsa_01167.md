# [H] Cross-Site Scripting in lazysizes

## Summary
Severity: High
Advisory: GHSA-w4vp-3mq7-7v82
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-w4vp-3mq7-7v82
Type: github-advisory

## Affected
- npm: `lazysizes` — affected >=0 <5.2.1-rc1

## Details
Versions of `lazysizes` prior to 5.2.1-rc1 are vulnerable to Cross-Site Scripting.  The `video-embed` plugin fails to sanitize the following attributes: data-vimeo, `data-vimeoparams`, `data-youtube` and `data-ytparams`. This allows attackers to execute arbitrary JavaScript in a victim's browser if the attacker has control over the vulnerable attributes.


## Recommendation

Upgrade to version 5.2.1-rc1 or later.

## References
- https://github.com/aFarkas/lazysizes/issues/764
- https://www.npmjs.com/advisories/1493
