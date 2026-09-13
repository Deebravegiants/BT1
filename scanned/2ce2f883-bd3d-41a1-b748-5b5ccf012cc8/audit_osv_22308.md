# [H] FreeRDP Server authentication might allow invalid credentials to pass

## Summary
Severity: High
Advisory: CVE-2022-24883
Aliases: GHSA-qxm3-v2r6-vmwf
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-04-26
Source: https://osv.dev/vulnerability/CVE-2022-24883
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP). Prior to version 2.7.0, server side authentication against a `SAM` file might be successful for invalid credentials if the server has configured an invalid `SAM` file path. FreeRDP based clients are not affected. RDP server implementations using FreeRDP to authenticate against a `SAM` file are affected. Version 2.7.0 contains a fix for this issue. As a workaround, use custom authentication via `HashCallback` and/or ensure the `SAM` database path configured is valid and the application has file handles left.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/2.7.0
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24883.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qxm3-v2r6-vmwf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AELSWWBAM2YONRPGLWVDY6UNTLJERJYL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DOYKBQOHSRM7JQYUIYUWFOXI2JZ2J5RD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PZWR6KSIKXO4B2TXBB3WH6YTNYHN46OY/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24883
- https://security.gentoo.org/glsa/202210-24
- https://github.com/FreeRDP/FreeRDP/commit/4661492e5a617199457c8074bad22f766a116cdc
- https://github.com/FreeRDP/FreeRDP/commit/6f473b273a4b6f0cb6aca32b95e22fd0de88e144
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
