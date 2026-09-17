# [H] BIT-mybb-2022-39265

## Summary
Severity: High
Advisory: BIT-mybb-2022-39265
Aliases: CVE-2022-39265, GHSA-hxhm-rq9f-7xj7
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mybb-2022-39265
Type: osv

## Affected
- Bitnami: `mybb` — affected >=0 <1.8.31

## Details
MyBB is a free and open source forum software. The _Mail Settings_ → Additional Parameters for PHP's mail() function mail_parameters setting value, in connection with the configured mail program's options and behavior, may allow access to sensitive information and Remote Code Execution (RCE). The vulnerable module requires Admin CP access with the `_Can manage settings?_` permission and may depend on configured file permissions. MyBB 1.8.31 resolves this issue with the commit `0cd318136a`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/mybb/mybb/blob/mybb_1830/install/resources/settings.xml#L2331-L2338
- https://github.com/mybb/mybb/commit/0cd318136a10b029bb5c8a8f6dddf39d87519797
- https://github.com/mybb/mybb/security/advisories/GHSA-hxhm-rq9f-7xj7
- https://mybb.com/versions/1.8.31/
