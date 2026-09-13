# [M] Improper Neutralization of Special Elements vulnerability in EJBCA

## Summary
Severity: Medium
Advisory: BIT-ejbca-2025-3026
Aliases: CVE-2025-3026
Ecosystem: Bitnami
Published: 2025-10-10
Source: https://osv.dev/vulnerability/BIT-ejbca-2025-3026
Type: osv

## Affected
- Bitnami: `ejbca` — affected >=8.0.0 <9.1.0

## Details
The vulnerability exists in the EJBCA service, version 8.0 Enterprise. Not tested in higher versions. By modifying the ‘Host’ header in an HTTP request, it is possible to manipulate the generated links and thus redirect the client to a different base URL.  In this way, an attacker could insert his own server for the client to send HTTP requests, provided he succeeds in exploiting it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3026
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-ejbca
