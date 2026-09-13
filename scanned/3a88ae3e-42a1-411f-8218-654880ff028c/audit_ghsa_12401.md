# [H] Unauthenticated Denial of Service in the octokit/webhooks library

## Summary
Severity: High
Advisory: GHSA-pwfr-8pq7-x9qv
CVE: CVE-2023-50728
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-12-16
Source: https://github.com/advisories/GHSA-pwfr-8pq7-x9qv
Type: github-advisory

## Affected
- npm: `@octokit/webhooks` — affected >=0 <9.26.3
- npm: `@octokit/webhooks` — affected >=10.0.0 <10.9.2
- npm: `@octokit/webhooks` — affected >=11.0.0 <11.1.2
- npm: `@octokit/webhooks` — affected >=12.0.0 <12.0.3
- npm: `@octokit/app` — affected >=14.0.1 <14.0.2
- npm: `octokit` — affected >=0 <3.1.2
- npm: `probot` — affected >=0 <12.3.3

## Details
### Impact
Versions [v9.26.0](https://github.com/octokit/webhooks.js/releases/tag/v9.26.0), [v10.9.x](https://github.com/octokit/webhooks.js/releases/tag/v10.9.1)), [v11.1.x](https://github.com/octokit/webhooks.js/releases/tag/v11.1.1), [v12.0.x](https://github.com/octokit/webhooks.js/releases/tag/v12.0.3) all contained the code that would throw the error.

Specifically, during a pentest we encountered a bug in the octokit/webhooks library (a dependency of Probot, a framework for building Github Apps). The resulting request was found to cause an uncaught exception that ends the nodejs process.

The problem is caused by an issue with error handling in the @octokit/webhooks library because the error can be undefined in some cases.

Credit goes to @pb82 (for the early analysis) and @rh-tguittet (for discovery). 

### Patches

Maintenance releases for the Error being thrown by the verify method in [octokit/webhooks.js](https://github.com/octokit/webhooks.js)
* v12 - [v12.0.4](https://github.com/octokit/webhooks.js/releases/tag/v12.0.4)
* v11 - [v11.1.2](https://github.com/octokit/webhooks.js/releases/tag/v11.1.2)
* v10 -[v10.9.2](https://github.com/octokit/webhooks.js/releases/tag/v10.9.2)
* v9 - [v9.26.3](https://github.com/octokit/webhooks.js/releases/tag/v9.26.3)

Maintenance release for the reference for [octokit/webhooks.js](https://github.com/octokit/webhooks.js) in [app.js](https://github.com/octokit/app.js)
* [v14.0.2](https://github.com/octokit/app.js/releases/tag/v14.0.2)

Maintenance release for the reference for [octokit/webhooks.js](https://github.com/octokit/webhooks.js) in [octokit.js](https://github.com/octokit/octokit.js)
* [v3.1.2](https://github.com/octokit/octokit.js/releases/tag/v3.1.2)

Maintenance release for the reference for [octokit/webhooks.js](https://github.com/octokit/webhooks.js) in [Protobot](https://github.com/probot/probot)
* [v12.3.3](https://github.com/probot/probot/releases/tag/v12.3.3)


### Workarounds
It is recommend that all users upgrade to the latest version of  [octokit/webhooks.js](https://github.com/octokit/webhooks.js) or use one of the updated back ported versions.

## References
- https://github.com/octokit/webhooks.js/security/advisories/GHSA-pwfr-8pq7-x9qv
- https://nvd.nist.gov/vuln/detail/CVE-2023-50728
- https://github.com/octokit/app.js/releases/tag/v14.0.2
- https://github.com/octokit/octokit.js/releases/tag/v3.1.2
- https://github.com/octokit/webhooks.js
- https://github.com/octokit/webhooks.js/releases/tag/v10.9.2
- https://github.com/octokit/webhooks.js/releases/tag/v11.1.2
- https://github.com/octokit/webhooks.js/releases/tag/v12.0.4
- https://github.com/octokit/webhooks.js/releases/tag/v9.26.3
- https://github.com/probot/probot/releases/tag/v12.3.3
