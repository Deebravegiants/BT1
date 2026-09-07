# [H] H2O Vulnerable to Denial of Service (DoS) via `HEAD` Request

## Summary
Severity: High
Advisory: GHSA-5c8j-g96x-cj78
CVE: CVE-2024-8062
CWE: CWE-1088
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-5c8j-g96x-cj78
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=3.2.0.1
- Maven: `ai.h2o:h2o-core` — affected >=3.2.0.1

## Details
A vulnerability in the typeahead endpoint of h2oai/h2o-3 version 3.46.0 allows for a denial of service. The endpoint performs a `HEAD` request to verify the existence of a specified resource without setting a timeout. An attacker can exploit this by sending multiple requests to an attacker-controlled server that hangs, causing the application to block and become unresponsive to other requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8062
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/047a4d617240a56e74f834207c65973d133391cb/h2o-core/src/main/java/water/persist/PersistManager.java#L302
- https://huntr.com/bounties/a04190d9-4acb-449a-9a7f-f1bf6be1ed23
