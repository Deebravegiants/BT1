# [H] Pac4j token validation bypass if OpenID Connect provider supports none algorithm

## Summary
Severity: High
Advisory: GHSA-xhw6-hjc9-679m
CVE: CVE-2021-44878
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-xhw6-hjc9-679m
Type: github-advisory

## Affected
- Maven: `org.pac4j:pac4j-oidc` — affected >=0 <4.5.5
- Maven: `org.pac4j:pac4j-oidc` — affected >=5.0 <5.3.1

## Details
If an OpenID Connect provider supports the “none” algorithm (i.e., tokens with no signature), pac4j v5.3.0 (and prior) does not refuse it without an explicit configuration on its side or for the “idtoken” response type which is not secure and violates the OpenID Core Specification. The "none" algorithm does not require any signature verification when validating the ID tokens, which allows the attacker to bypass the token validation by injecting a malformed ID token using "none" as the value of "alg" key in the header with an empty signature value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44878
- https://github.com/pac4j/pac4j/commit/09684e0de1c4753d22c53b8135d4ef61cfda76f7
- https://github.com/pac4j/pac4j/commit/22b82ffd702a132d9f09da60362fc6264fc281ae
- https://github.com/pac4j/pac4j/commit/9c87bbc536ed5d05f940ae015403120df2935589
- https://github.com/pac4j/pac4j
- https://openid.net/specs/openid-connect-core-1_0.html#IDToken
- https://www.pac4j.org/4.5.x/docs/release-notes.html
- https://www.pac4j.org/blog/cve_2021_44878_is_this_serious.html
