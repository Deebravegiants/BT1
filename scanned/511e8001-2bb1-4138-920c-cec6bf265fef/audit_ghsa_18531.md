# [M] Apache Commons Lang is vulnerable to Uncontrolled Recursion when processing long inputs

## Summary
Severity: Medium
Advisory: GHSA-j288-q9x7-2f5v
CVE: CVE-2025-48924
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-11
Source: https://github.com/advisories/GHSA-j288-q9x7-2f5v
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-lang3` — affected >=3.0 <3.18.0
- Maven: `commons-lang:commons-lang` — affected >=2.0

## Details
Uncontrolled Recursion vulnerability in Apache Commons Lang.

This issue affects Apache Commons Lang: Starting with commons-lang:commons-lang 2.0 to 2.6, and, from org.apache.commons:commons-lang3 3.0 before 3.18.0.

The methods ClassUtils.getClass(...) can throw StackOverflowError on very long inputs. Because an Error is usually not handled by applications and libraries, a StackOverflowError could cause an application to stop.

Users are recommended to upgrade to version 3.18.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48924
- https://github.com/apache/commons-lang/commit/b424803abdb2bec818e4fbcb251ce031c22aca53
- https://github.com/apache/commons-lang
- https://lists.apache.org/thread/bgv0lpswokgol11tloxnjfzdl7yrc1g1
- https://lists.debian.org/debian-lts-announce/2025/08/msg00000.html
- https://lists.debian.org/debian-lts-announce/2025/08/msg00026.html
- https://lists.debian.org/debian-lts-announce/2025/09/msg00032.html
- https://lists.debian.org/debian-lts-announce/2025/09/msg00036.html
- http://www.openwall.com/lists/oss-security/2025/07/11/1
