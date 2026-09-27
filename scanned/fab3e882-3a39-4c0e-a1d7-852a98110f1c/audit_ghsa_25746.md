# [C] Improper Restriction of XML External Entity Reference in com.monitorjbl:xlsx-streamer

## Summary
Severity: Critical
Advisory: GHSA-xvm2-9xvc-hx7f
CVE: CVE-2022-23640
CWE: CWE-611, CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-02
Source: https://github.com/advisories/GHSA-xvm2-9xvc-hx7f
Type: github-advisory

## Affected
- Maven: `com.monitorjbl:xlsx-streamer` — affected >=0 <2.1.0

## Details
### Impact
Prior to xlsx-streamer 2.1.0, the XML parser that was used did not apply all the necessary settings to prevent XML Entity Expansion issues.

### Patches
Upgrade to version 2.1.0.

### Workarounds
No known workaround.

### References
https://github.com/monitorjbl/excel-streaming-reader/commit/0749c7b9709db078ccdeada16d46a34bc2910c73

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [monitorjbl/excel-streaming-reader](https://github.com/monitorjbl/excel-streaming-reader)

## References
- https://github.com/monitorjbl/excel-streaming-reader/security/advisories/GHSA-xvm2-9xvc-hx7f
- https://nvd.nist.gov/vuln/detail/CVE-2022-23640
- https://github.com/monitorjbl/excel-streaming-reader/commit/0749c7b9709db078ccdeada16d46a34bc2910c73
- https://github.com/monitorjbl/excel-streaming-reader
