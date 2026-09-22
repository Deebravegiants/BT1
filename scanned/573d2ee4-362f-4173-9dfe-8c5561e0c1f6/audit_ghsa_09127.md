# [M] MindsDB has an Improper Access Control Issue

## Summary
Severity: Medium
Advisory: GHSA-9f6m-65v9-x9g2
CVE: CVE-2026-7711
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-9f6m-65v9-x9g2
Type: github-advisory

## Affected
- PyPI: `MindsDB` — affected >=0

## Details
A weakness has been identified in MindsDB up to 26.01. This impacts the function exec of the file mindsdb/integrations/handlers/byom_handler/proc_wrapper.py of the component Engine Handler. Executing a manipulation can lead to unrestricted upload. The attack can be executed remotely. The exploit has been made available to the public and could be used for attacks. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7711
- https://github.com/mindsdb/mindsdb
- https://github.com/nn0nkey/JD-Security-SHENYI-Team/blob/main/MindsDB_BYOM_RCE.md
- https://vuldb.com/submit/806822
- https://vuldb.com/vuln/360887
- https://vuldb.com/vuln/360887/cti
