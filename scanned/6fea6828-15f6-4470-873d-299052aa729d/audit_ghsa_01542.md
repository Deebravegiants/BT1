# [M] Potentially sensitive data exposure in Symfony Web Socket Bundle

## Summary
Severity: Medium
Advisory: GHSA-wwgf-3xp7-cxj4
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-wwgf-3xp7-cxj4
Type: github-advisory

## Affected
- Packagist: `gos/web-socket-bundle` — affected >=0 <1.10.4
- Packagist: `gos/web-socket-bundle` — affected >=2.0.0 <2.6.1
- Packagist: `gos/web-socket-bundle` — affected >=3.0.0 <3.3.0

## Details
### Impact
Inside `Gos\Bundle\WebSocketBundle\Server\App\Dispatcher\TopicDispatcher::onPublish()`, messages are arbitrarily broadcasted to the related Topic if `Gos\Bundle\WebSocketBundle\Server\App\Dispatcher\TopicDispatcher::dispatch()` does not succeed.  The `dispatch()` method can be considered to not succeed if (depending on the version of the bundle) the callback defined on a topic route is misconfigured, a `Gos\Bundle\WebSocketBundle\Topic\TopicInterface` implementation is not found for the callback, a topic which also implements `Gos\Bundle\WebSocketBundle\Topic\SecuredTopicInterface` rejects the connection, or an Exception is unhandled.  This can result in an unintended broadcast to the websocket server potentially with data that should be considered sensitive.

### Patches
In 1.10.4, 2.6.1, and 3.3.0, `Gos\Bundle\WebSocketBundle\Server\App\Dispatcher\TopicDispatcher::onPublish()` has been changed to no longer broadcast an event's data if `Gos\Bundle\WebSocketBundle\Server\App\Dispatcher\TopicDispatcher::dispatch()` fails.

### Workarounds
Upgrade to 1.10.4, 2.6.1, and 3.3.0

Note, the 1.x branch is considered end of support as of July 1, 2020.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [this repository](https://github.com/GeniusesOfSymfony/WebSocketBundle)

## References
- https://github.com/GeniusesOfSymfony/WebSocketBundle/security/advisories/GHSA-wwgf-3xp7-cxj4
- https://github.com/FriendsOfPHP/security-advisories/commit/942fd37245cb724ba8cc8d6f11f075a1bd53b338
- https://github.com/GeniusesOfSymfony/WebSocketBundle
- https://snyk.io/vuln/SNYK-PHP-GOSWEBSOCKETBUNDLE-575401
