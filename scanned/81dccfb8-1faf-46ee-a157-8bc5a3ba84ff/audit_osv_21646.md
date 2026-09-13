# [H] CVE-2021-44758

## Summary
Severity: High
Advisory: CVE-2021-44758
Aliases: GHSA-69h9-669w-88xv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-26
Source: https://osv.dev/vulnerability/CVE-2021-44758
Type: osv

## Details
Heimdal before 7.7.1 allows attackers to cause a NULL pointer dereference in a SPNEGO acceptor via a preferred_mech_type of GSS_C_NO_OID and a nonzero initial_response value to send_accept.

## References
- https://github.com/heimdal/heimdal/security/advisories/GHSA-69h9-669w-88xv
- https://security.gentoo.org/glsa/202310-06
- https://github.com/heimdal/heimdal/commit/f9ec7002cdd526ae84fbacbf153162e118f22580
