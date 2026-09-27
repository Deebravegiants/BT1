# [H] Denial of Service (DoS) in open-webui/open-webui

## Summary
Severity: High
Advisory: CVE-2024-12534
Aliases: GHSA-g3mx-83mp-3rwc, PYSEC-2026-1733
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12534
Type: osv

## Details
In version v0.3.32 of open-webui/open-webui, the application allows users to submit large payloads in the email and password fields during the sign-in process due to the lack of character length validation on these inputs. This vulnerability can lead to a Denial of Service (DoS) condition when a user submits excessively large strings, exhausting server resources such as CPU, memory, and disk space, and rendering the service unavailable for legitimate users. This makes the server susceptible to resource exhaustion attacks without requiring authentication.

## References
- https://huntr.com/bounties/c7c0a4e6-acd3-49b4-8684-2c2c27014b76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12534.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12534
