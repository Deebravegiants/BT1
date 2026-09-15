# [H] In MIT Kerberos 5 (aka krb5) before 1.22.3, there is a NULL pointer dereference if an application...

## Summary
Severity: High
Advisory: JLSEC-2026-1258
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1258
Type: osv

## Affected
- Julia: `Kerberos_krb5_jll` — affected unspecified

## Details
In MIT Kerberos 5 (aka krb5) before 1.22.3, there is a NULL pointer dereference if an application calls `gss_accept_sec_context()` on a system with a NegoEx mechanism registered in `/etc/gss/mech`. An unauthenticated remote attacker can trigger this, causing the process to terminate in `parse_nego_message`.

## References
- https://cems.fun/2026/04/27/krb5-two-unauthenticated-network-vulnerabilities.html
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/advisories/GHSA-8qgv-wm66-hrmc
- https://github.com/krb5/krb5/commit/2e75f0d9362fb979f5fc92829431a590a130929f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40355
- https://web.mit.edu/kerberos/advisories
- https://web.mit.edu/kerberos/advisories/
