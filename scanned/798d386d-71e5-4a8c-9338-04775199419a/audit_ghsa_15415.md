# [M] CometVisu Backend for openHAB has a path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pcwp-26pw-j98w
CVE: CVE-2024-42468
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-pcwp-26pw-j98w
Type: github-advisory

## Affected
- Maven: `org.openhab.ui.bundles:org.openhab.ui.cometvisu` — affected >=0 <4.2.1

## Details
openHAB's [CometVisuServlet](https://github.com/openhab/openhab-webui/blob/1c03c60f84388b9d7da0231df2d4ebb1e17d3fcf/bundles/org.openhab.ui.cometvisu/src/main/java/org/openhab/ui/cometvisu/internal/servlet/CometVisuServlet.java#L75) is susceptible to an unauthenticated path traversal vulnerability.

Local files on the server can be requested via HTTP GET on the CometVisuServlet.

This vulnerability was discovered with the help of CodeQL's [Uncontrolled data used in path expression](https://codeql.github.com/codeql-query-help/java/java-path-injection/) query.

## Impact

This issue may lead to Information Disclosure.

## References
- https://github.com/openhab/openhab-webui/security/advisories/GHSA-pcwp-26pw-j98w
- https://nvd.nist.gov/vuln/detail/CVE-2024-42468
- https://github.com/openhab/openhab-webui/commit/630e8525835c698cf58856aa43782d92b18087f2
- https://github.com/openhab/openhab-webui
- https://github.com/openhab/openhab-webui/blob/1c03c60f84388b9d7da0231df2d4ebb1e17d3fcf/bundles/org.openhab.ui.cometvisu/src/main/java/org/openhab/ui/cometvisu/internal/servlet/CometVisuServlet.java#L75
