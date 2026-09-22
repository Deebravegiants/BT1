# [M] Aim vulnerable to Synchronous Access of Remote Resource without Timeout

## Summary
Severity: Medium
Advisory: GHSA-v5pj-jrpv-h6g2
CVE: CVE-2024-12777
CWE: CWE-1088
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-v5pj-jrpv-h6g2
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
A vulnerability in aimhubio/aim version 3.25.0 allows for a denial of service through the misuse of the sshfs-client. The tracking server, which is single-threaded, can be made unresponsive by requesting it to connect to an unresponsive socket via sshfs. The lack of an additional timeout setting in the sshfs-client causes the server to hang for a significant amount of time, preventing it from responding to other requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12777
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/d4ad66ac87606b1f377d3e685e861abb2eef6c45/aim/ext/sshfs/utils.py#L151-L154
- https://huntr.com/bounties/cdf8db79-c290-4fe5-9383-4c518bfba4a8
