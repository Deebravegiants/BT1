# [H] Unauthenticated Denial of Service in open-webui/open-webui

## Summary
Severity: High
Advisory: CVE-2024-12537
Aliases: GHSA-chf7-q7m5-fq92, PYSEC-2026-1728
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12537
Type: osv

## Details
In version 0.3.32 of open-webui/open-webui, the absence of authentication mechanisms allows any unauthenticated attacker to access the `api/v1/utils/code/format` endpoint. If a malicious actor sends a POST request with an excessively high volume of content, the server could become completely unresponsive. This could lead to severe performance issues, causing the server to become unresponsive or experience significant degradation, ultimately resulting in service interruptions for legitimate users.

## References
- https://huntr.com/bounties/edabd06c-acc0-428c-a481-271f333755bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12537.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12537
