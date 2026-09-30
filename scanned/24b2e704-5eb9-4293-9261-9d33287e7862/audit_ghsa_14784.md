# [M] Zendframework session validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-62f6-h68r-3jpw
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-62f6-h68r-3jpw
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.2.9
- Packagist: `zendframework/zendframework` — affected >=2.3.0 <2.3.4

## Details
`Zend\Session` session validators do not work as expected if set prior to the start of a session.

For instance, the following test case fails (where `$this->manager` is an instance of `Zend\Session\SessionManager`):
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

An attacker is thus able to simply ignore session validators such as RemoteAddr or HttpUserAgent, since the "signature" that these validators check against is not being stored in the session.

## References
- https://github.com/zendframework/zendframework/commit/1672aee3531205e5c1a0b96d8c680124ec93db09
- https://github.com/zendframework/zendframework/commit/282135561cbf98cc93274c57966b021fd6e051b9
- https://github.com/zendframework/zendframework/commit/5f06a1f80a1aaeac87a46bfa9b63a5a74a14866c
- https://github.com/zendframework/zendframework/commit/9493d725ef869e6ce7ab78167539223396fda491
- https://github.com/zendframework/zendframework/commit/ddbf43ac3fe28fe98a4104993d0cb4bffb13a026
- https://github.com/zendframework/zendframework/commit/f22a83c611732fbc0328f0f887bccc075be1fd56
- https://framework.zend.com/security/advisory/ZF2015-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2015-01.yaml
- https://github.com/zendframework/zendframework
