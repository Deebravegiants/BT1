# [C] Lektor does not sanitize database path traversal

## Summary
Severity: Critical
Advisory: GHSA-wv28-7fpw-fj49
CVE: CVE-2024-28335
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-27
Source: https://github.com/advisories/GHSA-wv28-7fpw-fj49
Type: github-advisory

## Affected
- PyPI: `Lektor` — affected >=0 <3.3.11
- PyPI: `Lektor` — affected >=3.4.0b1 <3.4.0b11

## Details
Lektor before 3.3.11 does not sanitize DB path traversal. Thus, shell commands might be executed via a file that is added to the templates directory, if the victim's web browser accesses an untrusted website that uses JavaScript to send requests to localhost port 5000, and the web browser is running on the same machine as the "lektor server" command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28335
- https://github.com/lektor/lektor/pull/1179/commits/8f38b9713d152622b69ff5e3b1e6a0d7bb7fa800
- https://github.com/lektor/lektor/commit/7393d87bd354e43120937789956175064e4610a0
- https://brave.com/privacy-updates/27-localhost-permission
- https://cxsecurity.com/issue/WLB-2024030043
- https://getlektor.com/docs/quickstart
- https://github.com/lektor/lektor/releases/tag/v3.3.11
- https://github.com/pypa/advisory-database/tree/main/vulns/lektor/PYSEC-2024-49.yaml
- https://packetstormsecurity.com/files/177708/Lektor-Static-CMS-3.3.10-Arbitrary-File-Upload-Remote-Code-Execution.html
