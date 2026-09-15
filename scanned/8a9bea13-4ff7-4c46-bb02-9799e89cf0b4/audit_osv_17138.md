# [H] CVE-2020-12845

## Summary
Severity: High
Advisory: CVE-2020-12845
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-27
Source: https://osv.dev/vulnerability/CVE-2020-12845
Type: osv

## Details
Cherokee 0.4.27 to 1.2.104 is affected by a denial of service due to a NULL pointer dereferences. A remote unauthenticated attacker can crash the server by sending an HTTP request to protected resources using a malformed Authorization header that is mishandled during a cherokee_buffer_add call within cherokee_validator_parse_basic or cherokee_validator_parse_digest.

## References
- http://cherokee-project.com/downloads.html
- https://github.com/cherokee/webserver/releases
- https://security.gentoo.org/glsa/202012-09
- https://github.com/cherokee/webserver/issues/1242
