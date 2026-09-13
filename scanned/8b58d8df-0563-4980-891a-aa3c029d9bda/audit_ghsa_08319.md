# [H] changedetection.io project has an XXE vulnerability

## Summary
Severity: High
Advisory: GHSA-v7cp-2cx9-x793
CVE: CVE-2026-41895
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-v7cp-2cx9-x793
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0

## Details
# changedetection.io_XXE_01 Vulnerability Report: We discovered a XXE vulnerability in the changedetection.io project

While analyzing the code logic, it was determined that an area may lead to unintended behavior under specific conditions. With the project's security in mind, see the analysis results to discern whether this may indicate a potential security risk.

## Overview
- SOURCE_VERSION: `0.54.9 (9f3a9fdc18bba404244801e5df8109e213ce9ff4)`
- Vulnerability type: `XXE`
- Finding title: `XML XPath helpers parse untrusted XML with entity resolution left to lxml defaults`
- Affected location: `changedetectionio/html_tools.py:287`

## Root Cause
`xpath_filter()` switches to XML mode for XML/RSS content and creates `etree.XMLParser(strip_cdata=False)` without explicitly disabling external entity resolution, external DTD loading, or network-backed entity lookup. The helper then parses untrusted XML bytes directly with `etree.fromstring(...)`.

## Source-to-Sink Chain
1. Untrusted XML/RSS response content is fetched from monitored URLs.
2. Stream detection marks the content as XML/RSS and the include-filter path invokes `xpath_filter(..., is_xml=True)`.
3. `xpath_filter()` builds the default XML parser and calls `etree.fromstring(...)` at `changedetectionio/html_tools.py:287`.
4. External entity declarations in attacker XML can be expanded by parser-default behavior in affected runtime combinations.

## Exploitation Preconditions
1. Attacker controls the watched XML/RSS response body.
2. The watch uses an XPath include filter that triggers XML helper parsing.
3. Runtime parser behavior allows external entity expansion (for example, vulnerable dependency/default combinations).
4. The process can read the referenced local resource.

## Risk
The XML helper path can turn watch processing into a local file disclosure primitive when entity expansion is enabled by parser defaults.

## Impact
Sensitive local files can be exposed into extracted watch output, diff history, and downstream notification channels.

## Remediation
1. Harden XML parser construction with `resolve_entities=False`, `load_dtd=False`, and `no_network=True`.
2. Reject `DOCTYPE`/entity declarations for untrusted XML if DTD features are unnecessary.
3. Add regression tests that assert external entities are never expanded in XPath XML helper flows.

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-v7cp-2cx9-x793
- https://nvd.nist.gov/vuln/detail/CVE-2026-41895
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/pypa/advisory-database/tree/main/vulns/changedetection-io/PYSEC-2026-29.yaml
