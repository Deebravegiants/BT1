# [M] CVE-2020-26877

## Summary
Severity: Medium
Advisory: CVE-2020-26877
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-06-29
Source: https://osv.dev/vulnerability/CVE-2020-26877
Type: osv

## Details
ApiFest OAuth 2.0 Server 0.3.1 does not validate the redirect URI in accordance with RFC 6749 and is susceptible to an open redirector attack. Specifically, it directly sends an authorization code to the redirect URI submitted with the authorization request, without checking whether the redirect URI is registered by the client who initiated the request. This allows an attacker to craft a request with a manipulated redirect URI (redirect_uri parameter), which is under the attacker's control, and consequently obtain the leaked authorization code when the server redirects the client to the manipulated redirect URI with an authorization code. NOTE: this is similar to CVE-2019-3778.

## References
- http://www.apifest.org/index.html
- https://github.com/apifest/apifest-oauth20
- https://tools.ietf.org/html/rfc6749#section-3.1.2.3
