# [M] uutils coreutils chown and chgrp False Success Exit Code in Recursive Mode

## Summary
Severity: Medium
Advisory: CVE-2026-35340
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-35340
Type: osv

## Details
A flaw in the ChownExecutor used by uutils coreutils chown and chgrp causes the utilities to return an incorrect exit code during recursive operations. The final exit code is determined only by the last file processed. If the last operation succeeds, the command returns 0 even if earlier ownership or group changes failed due to permission errors. This can lead to security misconfigurations where administrative scripts incorrectly assume that ownership has been successfully transferred across a directory tree.

## References
- https://github.com/uutils
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35340.json
- https://github.com/uutils/coreutils/releases/tag/0.6.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-35340
- https://github.com/uutils/coreutils/pull/10035
- https://github.com/uutils/coreutils
