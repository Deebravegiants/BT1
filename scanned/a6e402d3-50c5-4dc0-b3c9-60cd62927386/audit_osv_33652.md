# [M] SSH_FXP_OPENDIR may Lead to Exhaustion of File Handles

## Summary
Severity: Medium
Advisory: CVE-2025-48041
Aliases: EEF-CVE-2025-48041, GHSA-79c4-cvv7-4qm3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-48041
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in Erlang OTP ssh (ssh_sftp modules) allows Excessive Allocation, Flooding. This vulnerability is associated with program files lib/ssh/src/ssh_sftpd.erl.

This issue affects OTP from OTP 17.0 before OTP 28.0.3, OTP 27.3.4.3 and OTP 26.2.5.15, corresponding to ssh from 3.0.1 before 5.3.3, 5.2.11.3 and 5.1.4.12.

## References
- https://cna.erlef.org/cves/CVE-2025-48041.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2025-48041
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48041.json
- https://github.com/erlang/otp/security/advisories/GHSA-79c4-cvv7-4qm3
- https://nvd.nist.gov/vuln/detail/CVE-2025-48041
- https://github.com/erlang/otp/commit/5f9af63eec4657a37663828d206517828cb9f288
- https://github.com/erlang/otp/commit/d49efa2d4fa9e6f7ee658719cd76ffe7a33c2401
- https://github.com/erlang/otp/pull/10157
- https://github.com/erlang/otp
