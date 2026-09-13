# [M] yii2-authclient vulnerable to possible timing attack on string comparison in OAuth1, OAuth2 and OpenID Connect implementation

## Summary
Severity: Medium
Advisory: CVE-2023-50708
Aliases: GHSA-w8vh-p74j-x9xp
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-50708
Type: osv

## Details
yii2-authclient is an extension that adds OpenID, OAuth, OAuth2 and OpenId Connect consumers for the Yii framework 2.0. In yii2-authclient prior to version 2.2.15, the Oauth1/2 `state` and OpenID Connect `nonce` is vulnerable for a `timing attack` since it is compared via regular string comparison (instead of `Yii::$app->getSecurity()->compareString()`). Version 2.2.15 contains a patch for the issue. No known workarounds are available.

## References
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OAuth1.php#L158
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OAuth2.php#L121
- https://github.com/yiisoft/yii2-authclient/blob/0d1c3880f4d79e20aa1d77c012650b54e69695ff/src/OpenIdConnect.php#L420
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50708.json
- https://github.com/yiisoft/yii2-authclient/security/advisories/GHSA-w8vh-p74j-x9xp
- https://nvd.nist.gov/vuln/detail/CVE-2023-50708
- https://github.com/yiisoft/yii2-authclient/commit/dabddf2154ab7e7703740205a069202554089248
