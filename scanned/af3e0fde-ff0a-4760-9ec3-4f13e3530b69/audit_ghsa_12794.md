# [H] RSSHub SSRF vulnerability

## Summary
Severity: High
Advisory: GHSA-64wp-jh9p-5cg2
CVE: CVE-2023-22493
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-64wp-jh9p-5cg2
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=0 <1.0.0-master.a66cbcf

## Details
## Summary

RSSHub is vulnerable to Server-Side Request Forgery (SSRF) attacks. This vulnerability allows an attacker to send arbitrary HTTP requests from the server to other servers or resources on the network.

## Description

An attacker can exploit this vulnerability by sending a request to the affected routes with a malicious URL. For example, if an attacker controls the `ATTACKER.HOST` domain, they can send a request to affected routes with the value set to `ATTACKER.HOST%2F%23`.
The `%2F` and `%23` characters are URL-encoded versions of the forward-slash (`/`) and pound (`#`) characters, respectively. In this context, an attacker could use those characters to append the base URL (i.e. `https://${input}.defined.host`) to be modified to `https://ATTACKER.HOST/#.defined.host`. This will cause the server to send a request to the attacker-controlled domain, allowing the attacker to potentially gain access to sensitive information or perform further attacks on the server. 

## Impact

An attacker could use this vulnerability to send requests to internal or any other servers or resources on the network, potentially gain access to sensitive information that would not normally be accessible and amplifying the impact of the attack.

## Reference

Fixing PR: https://github.com/DIYgod/RSSHub/pull/11588

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-64wp-jh9p-5cg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-22493
- https://github.com/DIYgod/RSSHub/pull/11588
- https://github.com/DIYgod/RSSHub/commit/a66cbcf6eebc700bf97ab097f404f16ab415506a
- https://advisory.dw1.io/56
- https://github.com/DIYgod/RSSHub
