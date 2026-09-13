# [H] Zendframework potential security issue in login mechanism

## Summary
Severity: High
Advisory: GHSA-9v78-h226-2rmq
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-9v78-h226-2rmq
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.4

## Details
Using the Consumer component of ZendOpenId (or Zend_OpenId in ZF1), it is possible to login using an arbitrary OpenID account (without knowing any secret information) by using a malicious OpenID Provider. That means OpenID it is possible to login using arbitrary OpenID Identity (MyOpenID, Google, etc), which are not under the control of our own OpenID Provider. Thus, we are able to impersonate any OpenID Identity against the framework.

Moreover, the Consumer accepts OpenID tokens with arbitrary signed elements. The framework does not check if, for example, both openid.claimed_id and openid.endpoint_url are signed. It is just sufficient to sign one parameter. According to https://openid.net/specs/openid-authentication-2_0.html#positive_assertions, at least op_endpoint, return_to, response_nonce, assoc_handle, and, if present in the response, claimed_id and identity, must be signed.

## References
- https://framework.zend.com/security/advisory/ZF2014-02
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2014-02.yaml
- https://github.com/zendframework/zf1
