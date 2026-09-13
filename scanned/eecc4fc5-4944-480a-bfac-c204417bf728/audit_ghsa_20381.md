# [M] Dev error stack trace leaking into prod in Play Framework

## Summary
Severity: Medium
Advisory: GHSA-p9p4-97g9-wcrh
CVE: CVE-2022-31023
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-p9p4-97g9-wcrh
Type: github-advisory

## Affected
- Maven: `com.typesafe.play:play_2.12` — affected >=0 <2.8.16
- Maven: `com.typesafe.play:play_2.13` — affected >=0 <2.8.16

## Details
### Impact

Play Framework, when run in dev mode, shows verbose errors for easy debugging, including an exception stack trace. Play does this by configuring its `DefaultHttpErrorHandler` to do so based on the application mode. In its Scala API Play also provides a static object `DefaultHttpErrorHandler` that is configured to always show verbose errors. This is used as a default value in some Play APIs, so it is possible to inadvertently use this version in production. It is also possible to improperly configure the `DefaultHttpErrorHandler` object instance as the injected error handler.  Both of these situations could result in verbose errors displaying to users in a production application, which could expose sensitive information from the application.

In particular the constructor for `CORSFilter` and `apply` method for `CORSActionBuilder` use the static object `DefaultHttpErrorHandler` as a default value.

### Patches

This is patched in Play Framework 2.8.16. The `DefaultHttpErrorHandler` object has been changed to use the prod-mode behavior, and `DevHttpErrorHandler` has been introduced for the dev-mode behavior.

### Workarounds

When constructing a `CORSFilter` or `CORSActionBuilder`, ensure that a properly-configured error handler is passed. Generally this should be done by using the `HttpErrorHandler` instance provided through dependency injection or through Play's `BuiltInComponents`. Ensure that your application is not using the `DefaultHttpErrorHandler` static object in any code that may be run in production.

### References
https://www.playframework.com/documentation/2.8.x/ScalaErrorHandling#Supplying-a-custom-error-handler
https://www.playframework.com/documentation/2.8.x/JavaErrorHandling#Supplying-a-custom-error-handler

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [playframework/playframework](https://github.com/playframework/playframework/)
* Email us at [security@playframework.com](mailto:security@playframework.com)

## References
- https://github.com/playframework/playframework/security/advisories/GHSA-p9p4-97g9-wcrh
- https://nvd.nist.gov/vuln/detail/CVE-2022-31023
- https://github.com/playframework/playframework/pull/11305
- https://github.com/playframework/playframework
- https://github.com/playframework/playframework/releases/tag/2.8.16
