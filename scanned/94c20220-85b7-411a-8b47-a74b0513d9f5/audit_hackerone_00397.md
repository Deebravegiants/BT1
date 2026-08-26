# [M] Race Conditions in OAuth 2 API implementations

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Improper Authentication - Generic
Reporter: dor1s
State: resolved
Disclosed: 2017-09-19T17:40:28.080Z
Source: https://hackerone.com/reports/55140

## Details
Most of OAuth 2 API implementations seem to have multiple Race Condition vulnerabilities for processing requests for Access Token or Refresh Token.

Race Condition allows a malicious application to obtain several `access_token` and `refresh_token` pairs while only one pair should be generated. Further, it leads to authorization bypass when access would be revoked.

I've already tested for this vulnerability 11 different targets (web-services providing OAuth2 API), and 6 of them are vulnerable. Only one target seems to be certainly protected (or I just failed to catch into Race Condition time window). The rest 4 targets have Race Condition bug, but protected against further exploitation by one of the following reasons:
* only one of several tokens generated is valid (**1 target**)
* for any access revocation all tokens always are revoked (**1 target**)
* for all concurring requests finished successfully the same `access_token` values (or in pair with `refresh_token`) obtained (**2 targets**)

At this moment I cannot list vulnerable targets here because of responsible disclosure, but I think it would be possible to publish their names soon.

Initially, I thought the vulnerability is located in [Doorkeeper gem for Ruby](https://github.com/doorkeeper-gem/doorkeeper). It is very popular, and I know that some of the vulnerable targets use this gem. To be clear, I tested [OAuth 2 provider example based on it](https://github.com/doorkeeper-gem/doorkeeper-provider-app) and it was safe for me. *Honestly, I'm not ruby developer, so it is not easy for me to quickly inspect doorkeeper's code and distinguish is it vulnerable or not*.

However, I'm sure that 6 of vulnerable targets use different implementations (at least more than one). So the attack vector seems to be universal and possible by design.

Race Condition for Access Token
===============================
According to [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749), `code` obtained via callback may be used only once to generate `access_token` (and corresponding `refresh_token`).

Race Condition vulnerability allows a malicious application to generate several `access_token` and `refresh_token` pairs. This leads to authentication issue when a user will revoke access for an application. One `access_token` and `refresh_token` pair would be revoked, but all the rest stay active.

Proof-Of-Concept
------------------------
 *PoC description is unified and may be used for any provider*

0) Register an application for using OAuth 2.0 API of the target provider. Obtain credentials for the application

1) Open link for the application authorization in browser. Usually it looks like:
```
https://OAUTH_PROVIDER_DOMAIN/oauth/authorize?client_id=APPLICATION_ID&redirect_uri=https://APPLICATION_REDIRECT_URI&response_type=code
```

2) Log into *a victim's* account (if it needed) and allow access for the application

3) Obtain `code` value from callback:
```
https://APPLICATION_REDIRECT_URI?code=AUTHORIZATION_CODE_VALUE
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/55140_
