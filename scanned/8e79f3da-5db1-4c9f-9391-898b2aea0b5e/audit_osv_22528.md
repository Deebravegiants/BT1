# [H] Prototype Pollution in underscore.deep

## Summary
Severity: High
Advisory: CVE-2022-31106
Aliases: GHSA-8j79-hfj5-f2xm
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2022-31106
Type: osv

## Details
Underscore.deep is a collection of Underscore mixins that operate on nested objects. Versions of `underscore.deep` prior to version 0.5.3 are vulnerable to a prototype pollution vulnerability. An attacker can craft a malicious payload and pass it to `deepFromFlat`, which would pollute any future Objects created. Any users that have `deepFromFlat` or `deepPick` (due to its dependency on `deepFromFlat`) in their code should upgrade to version 0.5.3 as soon as possible. Users unable to upgrade may mitigate this issue by modifying `deepFromFlat` to prevent specific keywords which will prevent this from happening.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31106.json
- https://github.com/Clever/underscore.deep/security/advisories/GHSA-8j79-hfj5-f2xm
- https://nvd.nist.gov/vuln/detail/CVE-2022-31106
- https://github.com/Clever/underscore.deep/commit/b5e109ad05b48371be225fa4d490dd08a94e8ef7
