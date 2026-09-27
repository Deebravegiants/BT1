# [C] CVE-2022-30935

## Summary
Severity: Critical
Advisory: CVE-2022-30935
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-30935
Type: osv

## Details
An authorization bypass in b2evolution allows remote, unauthenticated attackers to predict password reset tokens for any user through the use of a bad randomness function. This allows the attacker to get valid sessions for arbitrary users, and optionally reset their password. Tested and confirmed in a default installation of version 7.2.3. Earlier versions are affected, possibly earlier major versions as well.

## References
- https://b2evolution.net/downloads/7-2-5-stable
- https://github.com/b2evolution/b2evolution/blob/master/inc/_core/_misc.funcs.php#L5955
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30935.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30935
- https://github.com/b2evolution/b2evolution/issues/114
