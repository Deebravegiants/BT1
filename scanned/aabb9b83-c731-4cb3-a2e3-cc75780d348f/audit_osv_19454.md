# [C] CVE-2021-21335

## Summary
Severity: Critical
Advisory: CVE-2021-21335
Aliases: GHSA-ww8q-72rx-hc54
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-21335
Type: osv

## Details
In the SPNEGO HTTP Authentication Module for nginx (spnego-http-auth-nginx-module) before version 1.1.1 basic Authentication can be bypassed using a malformed username. This affects users of spnego-http-auth-nginx-module that have enabled basic authentication. This is fixed in version 1.1.1 of spnego-http-auth-nginx-module. As a workaround, one may disable basic authentication.

## References
- https://github.com/stnoonan/spnego-http-auth-nginx-module/releases/tag/v1.1.1
- https://github.com/stnoonan/spnego-http-auth-nginx-module/commit/a06f9efca373e25328b1c53639a48decd0854570
- https://github.com/stnoonan/spnego-http-auth-nginx-module/security/advisories/GHSA-ww8q-72rx-hc54
