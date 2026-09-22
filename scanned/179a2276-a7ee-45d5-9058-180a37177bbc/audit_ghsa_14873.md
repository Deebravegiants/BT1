# [M] Zend-Session session validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-96c6-m98x-hxjx
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-96c6-m98x-hxjx
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-session` — affected >=2.0.0 <2.2.9
- Packagist: `zendframework/zend-session` — affected >=2.3.0 <2.3.4

## Details
`Zend\Session` session validators do not work as expected if set prior to the start of a session.

For instance, the following test case fails (where $this->manager is an instance of `Zend\Session\SessionManager`):
```
$this
    ->manager
    ->getValidatorChain()
    ->attach('session.validate', array(new RemoteAddr(), 'isValid'));

$this->manager->start();

$this->assertSame(
    array(
        'Zend\Session\Validator\RemoteAddr' =3D> '',
    ),
    $_SESSION['__ZF']['_VALID']
);
```
The implication is that subsequent calls to `Zend\Session\SessionManager#start()` (in later requests, assuming a session was created) will not have any validator metadata attached, which causes any validator metadata to be re-built from scratch, thus marking the session as valid.

An attacker is thus able to simply ignore session validators such as `RemoteAddr` or `HttpUserAgent`, since the "signature" that these validators check against is not being stored in the session.

## References
- https://github.com/zendframework/zend-session/commit/05fa95488b5ade513c4dcc56051a7ddb1c94f341
- https://github.com/zendframework/zend-session/commit/1272fc047121720130690c324413629d8f63d210
- https://github.com/zendframework/zend-session/commit/35014ab0ae17c2a169320f182697ee9fe73d841e
- https://github.com/zendframework/zend-session/commit/3b1a65b3193a4219f5c4259ab8735f9ad254a021
- https://github.com/zendframework/zend-session/commit/6a27a9fddd8f5b12b3af0de6309181ff5946dd0e
- https://github.com/zendframework/zend-session/commit/7c4b73dd64e01001946aac76c6deddfe1c6ef0be
- https://github.com/zendframework/zend-session/commit/7fc94bd6a60342416242a3899d63072c471b33d3
- https://github.com/zendframework/zend-session/commit/93b43aa0ca5348d29034f67195ffa3f4082878d5
- https://github.com/zendframework/zend-session/commit/9868f84513536446b0bac81cc95e0130b0a6fc9c
- https://github.com/zendframework/zend-session/commit/a3382bfd3067f527762294b5fc622550988e6862
- https://github.com/zendframework/zend-session/commit/b1903947e285568344b3458e4524b016ce311072
- https://github.com/zendframework/zend-session/commit/ff9236cc4c4944b5f5a6fbfee01420ef82c4fa91
- https://framework.zend.com/security/advisory/ZF2015-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-session/ZF2015-01.yaml
- https://github.com/zendframework/zend-session
