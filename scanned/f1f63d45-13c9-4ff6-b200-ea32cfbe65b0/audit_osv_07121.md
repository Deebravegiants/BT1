# [M] BIT-node-2021-3672

## Summary
Severity: Medium
Advisory: BIT-node-2021-3672
Aliases: BIT-node-min-2021-3672, BIT-pgbouncer-2021-3672, CVE-2021-3672
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-3672
Type: osv

## Affected
- Bitnami: `node` — affected >=16.0.0 <16.6.2

## Details
A flaw was found in c-ares library, where a missing input validation check of host names returned by DNS (Domain Name Servers) can lead to output of wrong hostnames which might potentially lead to Domain Hijacking. The highest threat from this vulnerability is to confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1988342
- https://c-ares.haxx.se/adv_20210810.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://security.gentoo.org/glsa/202401-02
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-3672
