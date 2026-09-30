# [H] Argument Injection in RegionProtect

## Summary
Severity: High
Advisory: CVE-2022-29215
Aliases: GHSA-7gr2-w2r3-r9vf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-21
Source: https://osv.dev/vulnerability/CVE-2022-29215
Type: osv

## Details
RegionProtect is a plugin that allows users to manage certain events in certain regions of the world. Versions prior to 1.1.0 contain a YAML injection vulnerability that can cause an instant server crash if the passed arguments are not matched. Version 1.1.0 contains a patch for this issue. As a workaround, restrict operator permissions to untrusted people and avoid entering arguments likely to cause a crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29215.json
- https://github.com/kaidomc-pm-pl/RegionProtect/security/advisories/GHSA-7gr2-w2r3-r9vf
- https://nvd.nist.gov/vuln/detail/CVE-2022-29215
- https://github.com/kaidomc-pm-pl/RegionProtect/commit/0060d421358ab59acb6a168eab0d11c43d2d105d
