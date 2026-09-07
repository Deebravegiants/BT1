# [H] Bugsink affected by authenticated arbitrary file write in artifactbundle/assemble

## Summary
Severity: High
Advisory: GHSA-8hw4-fhww-273g
CVE: CVE-2026-40162
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8hw4-fhww-273g
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=2.1.0 <2.1.1

## Details
# Authenticated arbitrary file write in artifact bundle assembly

## Summary

An authenticated file write vulnerability was identified in Bugsink **2.1.0** in the artifact bundle assembly flow.

A user with a valid authentication token could cause the application to write attacker-controlled content to a filesystem location writable by the Bugsink process.

This issue requires authentication and affects only version **2.1.0**.

The issue is fixed in **2.1.1**.

## Impact

This vulnerability allows an authenticated user to create or overwrite files **within locations writable by the Bugsink service account**.

The practical impact depends on the deployment environment and filesystem permissions of the running process.

Possible consequences include:

* modification of application data files
* corruption of uploaded assets or temporary files
* overwriting files in mounted writable volumes
* disruption of normal application behavior

No unauthenticated exploitation is known.

No direct code execution has been demonstrated as part of this issue, though impact may be greater in deployments where the process has broad write permissions.

## Affected versions

* **Affected:** 2.1.0
* **Fixed:** 2.1.1
* **Not affected:** earlier releases

## Mitigation

Upgrade to **2.1.1**.

As a defense-in-depth measure, deployments should continue to ensure the Bugsink process runs with the **minimum required filesystem permissions**.

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-8hw4-fhww-273g
- https://nvd.nist.gov/vuln/detail/CVE-2026-40162
- https://github.com/bugsink/bugsink
- https://github.com/bugsink/bugsink/releases/tag/2.1.1
