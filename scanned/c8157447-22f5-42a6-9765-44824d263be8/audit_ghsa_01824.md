# [M] Vulnerable dependency in XTDB connector

## Summary
Severity: Medium
Advisory: GHSA-hwvm-vfw8-93mw
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-hwvm-vfw8-93mw
Type: github-advisory

## Affected
- Maven: `org.odpi.egeria:egeria-connector-xtdb` — affected >=0 <3.5

## Details
### Impact

The impacted portion of the XTDB connector is its connectivity to S3 as a backing store: this is the only portion of the connector that uses this vulnerable `httpclient` dependency. Per the description, the vulnerability regards URIs that may be misinterpreted, which given the area of impact within the connector we understand to be any URI used to configure connectivity to S3. Note therefore that if you do not use or configure S3 as a backing store in your use of the connector, you should not be exposed to any vulnerability from this component.

### Patches

The problem has been addressed in version 4.5.13 of the httpclient library, which is included as a replacement dependency version for the build of the XTDB connector from release 3.5 onwards. Therefore, using release 3.5 (or newer) of the connector will include the fixes to address this CVE.

### Workarounds

We have not investigated specific workarounds, but per the description of the issue it seems likely that ensuring the proper URIs are used for any S3 connectivity used by the connector (and ensuring there are appropriate controls around modifying such URIs in the connector's configuration) would be the first point of investigation.

### References

https://nvd.nist.gov/vuln/detail/CVE-2020-13956

## References
- https://github.com/odpi/egeria-connector-xtdb/security/advisories/GHSA-hwvm-vfw8-93mw
- https://nvd.nist.gov/vuln/detail/CVE-2020-13956
- https://github.com/odpi/egeria-connector-xtdb/commit/7b2dcc9fc6c5ce509cf72a275a2f2b8b1870dc15
- https://github.com/odpi/egeria-connector-xtdb
