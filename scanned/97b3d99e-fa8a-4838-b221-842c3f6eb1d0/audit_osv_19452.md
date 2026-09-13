# [C] CVE-2021-21329

## Summary
Severity: Critical
Advisory: CVE-2021-21329
Aliases: GHSA-fw57-f7mq-9q85
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-21329
Type: osv

## Details
RATCF is an open-source framework for hosting Cyber-Security Capture the Flag events. In affected versions of RATCF users with multi factor authentication enabled are able to log in without a valid token. This is fixed in commit cebb67b.

## References
- https://github.com/ractf/core/commit/c57a4d186bfc586ad3edfe4dcba9f11efbf22f09#diff-60c444c47c061306f2dff5bf97c07810f40f949a8e94ecbb609b6b29364c8642R130-R152
- https://github.com/ractf/core/commit/cebb67bd16a8296121201805332365ffccb29638
- https://github.com/ractf/core/security/advisories/GHSA-fw57-f7mq-9q85
