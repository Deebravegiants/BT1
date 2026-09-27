# [C] Remote Code Execution in esigate-core

## Summary
Severity: Critical
Advisory: GHSA-hjm9-576q-399p
CVE: CVE-2018-1000854
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-hjm9-576q-399p
Type: github-advisory

## Affected
- Maven: `org.esigate:esigate-core` — affected >=0 <5.3

## Details
esigate.org esigate version 5.2 and earlier contains a CWE-74: Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') vulnerability in ESI directive with user specified XSLT that can result in Remote Code Execution. This attack appear to be exploitable via Use of another weakness in backend application to reflect ESI directives. This vulnerability appears to have been fixed in 5.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000854
- https://github.com/esigate/esigate/issues/209
- https://github.com/advisories/GHSA-hjm9-576q-399p
- https://github.com/esigate/esigate
