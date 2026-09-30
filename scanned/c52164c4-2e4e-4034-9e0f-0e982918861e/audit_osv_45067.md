# [C] PYSEC-2024-74

## Summary
Severity: Critical
Advisory: PYSEC-2024-74
Aliases: CVE-2024-24759, GHSA-4jcv-vp96-94xr
Ecosystem: PyPI
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/PYSEC-2024-74
Type: osv

## Affected
- PyPI: `mindsdb` — affected >=0 <5f7496481bd3db1d06a2d2e62c0dce960a1fe12b, >=0 <23.12.4.2

## Details
MindsDB is a platform for building artificial intelligence from enterprise data. Prior to version 23.12.4.2, a threat actor can bypass the server-side request forgery protection on the whole website with DNS Rebinding. The vulnerability can also lead to denial of service. Version 23.12.4.2 contains a patch.

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-4jcv-vp96-94xr
- https://github.com/mindsdb/mindsdb/commit/5f7496481bd3db1d06a2d2e62c0dce960a1fe12b
