# [C] Remote code injection in Log4j

## Summary
Severity: Critical
Advisory: GHSA-94g7-hpv8-h9qm
Ecosystem: Maven
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-94g7-hpv8-h9qm
Type: github-advisory

## Affected
- Maven: `com.splunk.logging:splunk-library-javalogging` — affected >=1.7.0 <1.11.1
- Maven: `com.splunk.logging:splunk-library-javalogging` — affected >=0 <1.6.2-0-0

## Details
### Impact
Logging untrusted or user controlled data with a vulnerable version of Log4J may result in Remote Code Execution (RCE) against your application. This includes untrusted data included in logged errors such as exception traces, authentication failures, and other unexpected vectors of user controlled input.

More Details:
https://github.com/advisories/GHSA-jfh8-c2jp-5v3q

### Patches
Version 1.11.1 of the Splunk Logging for Java library.

There is also a backport to version 1.6.2 released as a patch: 1.6.2-0-0.

### Workarounds
If upgrading is not possible, then ensure the -Dlog4j2.formatMsgNoLookups=true system property is set on both client- and server-side components.

### References
https://github.com/advisories/GHSA-jfh8-c2jp-5v3q

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/splunk/splunk-library-javalogging/issues
* Email us at [devinfo@splunk.com](mailto:devinfo@splunk.com)

## References
- https://github.com/splunk/splunk-library-javalogging/security/advisories/GHSA-94g7-hpv8-h9qm
- https://github.com/splunk/splunk-library-javalogging
