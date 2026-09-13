# [M] CVE-2021-41185

## Summary
Severity: Medium
Advisory: CVE-2021-41185
Aliases: GHSA-252r-94ph-m229
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-26
Source: https://osv.dev/vulnerability/CVE-2021-41185
Type: osv

## Details
Mycodo is an environmental monitoring and regulation system. An exploit in versions prior to 8.12.7 allows anyone with access to endpoints to download files outside the intended directory. A patch has been applied and a release made. Users should upgrade to version 8.12.7. As a workaround, users may manually apply the changes from the fix commit.

## References
- https://github.com/kizniche/Mycodo/releases/tag/v8.12.7
- https://github.com/kizniche/Mycodo/issues/1105
- https://github.com/kizniche/Mycodo/commit/23ac5dd422029c2b6ae1701a3599b6d41b66a6a9
- https://github.com/kizniche/Mycodo/security/advisories/GHSA-252r-94ph-m229
