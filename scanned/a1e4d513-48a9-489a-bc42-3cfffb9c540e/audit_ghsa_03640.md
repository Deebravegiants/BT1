# [C] Failure to sanitize quotes which can lead to sql injection in squel

## Summary
Severity: Critical
Advisory: GHSA-4qhx-g9wp-g9m6
CWE: CWE-74, CWE-89
Ecosystem: npm
Published: 2019-06-14
Source: https://github.com/advisories/GHSA-4qhx-g9wp-g9m6
Type: github-advisory

## Affected
- npm: `squel` — affected >=0

## Details
All versions of `squel` are vulnerable to sql injection.

The `squel` package does not properly escape user provided input when provided using the `setFields` method. This could lead to sql injection if the query was then executed.

Proof of concept demonstrating the injection of a single quote into a generated sql statement from user provided input.
```
> console.log(squel.insert().into('buh').setFields({foo: "bar'baz"}).toString());
INSERT INTO buh (foo) VALUES ('bar'baz')
```


## Recommendation

There is no fix at this time and the issue has been reported publicly. Consider using another query builder that provides strong guarantees for input sanitization to prevent sql injection attacks.

## References
- https://github.com/hiddentao/squel/issues/350
- https://github.com/hiddentao/squel
- https://www.npmjs.com/advisories/575
