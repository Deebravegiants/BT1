# [H] Authentik lacks Proxy IP headers validation

## Summary
Severity: High
Advisory: BIT-authentik-2023-36456
Aliases: CVE-2023-36456, GHSA-cmxp-jcw7-jjjv
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2023-36456
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2023.5.0 <2023.5.5

## Details
authentik is an open-source Identity Provider. Prior to versions 2023.4.3 and 2023.5.5, authentik does not verify the source of the X-Forwarded-For and X-Real-IP headers, both in the Python code and the go code. Only authentik setups that are directly accessible by users without a reverse proxy are susceptible to this. Possible spoofing of IP addresses in logs, downstream applications proxied by (built in) outpost, IP bypassing in custom flows if used.

This poses a possible security risk when someone has flows or policies that check the user's IP address, e.g. when they want to ignore the user's 2 factor authentication when the user is connected to the company network. A second security risk is that the IP addresses in the logfiles and user sessions are not reliable anymore. Anybody can spoof this address and one cannot verify that the user has logged in from the IP address that is in their account's log. A third risk is that this header is passed on to the proxied application behind an outpost. The application may do any kind of verification, logging, blocking or rate limiting based on the IP address, and this IP address can be overridden by anybody that want to.

Versions 2023.4.3 and 2023.5.5 contain a patch for this issue.

## References
- https://github.com/goauthentik/authentik/commit/15026748d19d490eb2baf9a9566ead4f805f7dff
- https://github.com/goauthentik/authentik/commit/c07a48a3eccbd7b23026f72136d3392bbc6f795a
- https://github.com/goauthentik/authentik/security/advisories/GHSA-cmxp-jcw7-jjjv
- https://goauthentik.io/docs/releases/2023.4#fixed-in-202343
- https://goauthentik.io/docs/releases/2023.5#fixed-in-202355
- https://nvd.nist.gov/vuln/detail/CVE-2023-36456
