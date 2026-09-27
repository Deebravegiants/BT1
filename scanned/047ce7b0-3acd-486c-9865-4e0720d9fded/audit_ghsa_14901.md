# [H] ZendFramework Route Parameter Injection Via Query String in `Zend\Mvc`

## Summary
Severity: High
Advisory: GHSA-jq87-2wxp-8349
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-jq87-2wxp-8349
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.0.8
- Packagist: `zendframework/zendframework` — affected >=2.1.0 <2.1.4

## Details
In Zend Framework 2, `Zend\Mvc\Router\Http\Query` is used primarily to allow appending query strings to URLs when assembled. However, due to the fact that it captures any query parameters into the RouteMatch, and the fact that RouteMatch parameters are merged with any parent routes, this can lead to overriding already captured routing parameters, bypassing constraints defined in the parents.

As an example, consider the following route definition:
```
array(
    'user' => array(
        'type' => 'segment',
        'options' => array(
            'route' => '/user/:key',
            'defaults' => array(
                'controller' => 'UserController',
                'action'     => 'show-action',
            ),
            'constraints' => array(
                'key' => '[a-z0-9]+',
            ),
        ),
        'child_routes' => array(
            'query' => array('type' => 'query'),
        ),
    ),
)
```
If the request URI was /user/foo/?controller=SecretController&key=invalid_value, the RouteMatch returned after routing would contain the following:
```
array(
    'controller' => 'SecretController',
    'action'     => 'show-action',
    'key'        => 'invalid_value',
)
```
This would lead to execution of a different controller than intended, with a value for the key parameter that bypassed the constraints outlined in the parent route.

## References
- https://github.com/zendframework/zendframework/commit/0a7ec3407f02db29ea2ffd6daa71ead6fd151cfe
- https://github.com/zendframework/zendframework/commit/7fcb88ebc2d56f74aa943909f2b6b53f5c86b081
- https://framework.zend.com/security/advisory/ZF2013-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2013-01.yaml
- https://github.com/zendframework/zendframework
