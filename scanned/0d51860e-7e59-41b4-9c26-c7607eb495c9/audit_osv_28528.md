# [M] CVE-2024-34149

## Summary
Severity: Medium
Advisory: CVE-2024-34149
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-30
Source: https://osv.dev/vulnerability/CVE-2024-34149
Type: osv

## Details
In Bitcoin Core through 27.0 and Bitcoin Knots before 25.1.knots20231115, tapscript lacks a policy size limit check, a different issue than CVE-2023-50428. NOTE: some parties oppose this new limit check (for example, because they agree with the objective but disagree with the technical mechanism, or because they have a different objective).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34149.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34149
- https://github.com/bitcoin/bitcoin/pull/29769
