# [C] CVE-2020-1887

## Summary
Severity: Critical
Advisory: CVE-2020-1887
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-03-13
Source: https://osv.dev/vulnerability/CVE-2020-1887
Type: osv

## Details
Incorrect validation of the TLS SNI hostname in osquery versions after 2.9.0 and before 4.2.0 could allow an attacker to MITM osquery traffic in the absence of a configured root chain of trust.

## References
- https://www.facebook.com/security/advisories/cve-2020-1887
- https://github.com/osquery/osquery/pull/6197
