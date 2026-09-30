# [M] PYSEC-2024-32

## Summary
Severity: Medium
Advisory: PYSEC-2024-32
Aliases: CVE-2024-22193, GHSA-rjmv-52mp-gjrr
Ecosystem: PyPI
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-01-30
Source: https://osv.dev/vulnerability/PYSEC-2024-32
Type: osv

## Affected
- PyPI: `vantage6` — affected >=0 <6383283733b81abfcacfec7538dc4dc882e98074, >=0 <4.2.0

## Details
The vantage6 technology enables to manage and deploy privacy enhancing technologies like Federated Learning (FL) and Multi-Party Computation (MPC). There are no checks on whether the input is encrypted if a task is created in an encrypted collaboration. Therefore, a user may accidentally create a task with sensitive input data that will then be stored unencrypted in a database.  Users should ensure they set the encryption setting correctly.  This vulnerability is patched in 4.2.0.

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-rjmv-52mp-gjrr
- https://github.com/vantage6/vantage6/commit/6383283733b81abfcacfec7538dc4dc882e98074
