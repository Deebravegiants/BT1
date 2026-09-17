# [H] CVE-2020-15867

## Summary
Severity: High
Advisory: CVE-2020-15867
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-15867
Type: osv

## Details
The git hook feature in Gogs 0.5.5 through 0.12.2 allows for authenticated remote code execution. There can be a privilege escalation if access to this hook feature is granted to a user who does not have administrative privileges. NOTE: because this is mentioned in the documentation but not in the UI, it could be considered a "Product UI does not Warn User of Unsafe Actions" issue.

## References
- http://packetstormsecurity.com/files/162123/Gogs-Git-Hooks-Remote-Code-Execution.html
- https://www.fzi.de/en/news/news/detail-en/artikel/fsa-2020-3-schwachstelle-in-gitea-1125-und-gogs-0122-ermoeglicht-ausfuehrung-von-code-nach-authent/
