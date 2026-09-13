# [M] npm CLI exposing sensitive information through logs

## Summary
Severity: Medium
Advisory: GHSA-93f3-23rq-pjfp
CVE: CVE-2020-15095
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-93f3-23rq-pjfp
Type: github-advisory

## Affected
- npm: `npm` — affected >=0 <6.14.6

## Details
Versions of the npm CLI prior to 6.14.6 are vulnerable to an information exposure vulnerability through log files. The CLI supports URLs like `<protocol>://[<user>[:<password>]@]<hostname>[:<port>][:][/]<path>`. The password value is not redacted and is printed to stdout and also to any generated log files.

## References
- https://github.com/npm/cli/security/advisories/GHSA-93f3-23rq-pjfp
- https://nvd.nist.gov/vuln/detail/CVE-2020-15095
- https://github.com/npm/cli/commit/a9857b8f6869451ff058789c4631fadfde5bbcbc
- https://github.com/npm/cli/blob/66aab417f836a901f8afb265251f761bb0422463/CHANGELOG.md#6146-2020-07-07
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4OOYAMJVLLCLXDTHW3V5UXNULZBBK4O6
- https://security.gentoo.org/glsa/202101-07
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00023.html
