# [C] Remote Code Execution for 2.4.1 and earlier

## Summary
Severity: Critical
Advisory: GHSA-76f7-9v52-v2fw
CVE: CVE-2023-36812
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-76f7-9v52-v2fw
Type: github-advisory

## Affected
- Maven: `net.opentsdb:opentsdb` — affected >=0 <2.4.2

## Details
### Impact
OpenTSDB is vulnerable to Remote Code Execution vulnerability by writing user-controlled input to Gnuplot configuration file and running Gnuplot with the generated configuration.

### Patches
Patched in [07c4641471c6f5c2ab5aab615969e97211eb50d9](https://github.com/OpenTSDB/opentsdb/commit/07c4641471c6f5c2ab5aab615969e97211eb50d9) and further refined in https://github.com/OpenTSDB/opentsdb/commit/fa88d3e4b5369f9fb73da384fab0b23e246309ba

### Workarounds
Disable Gunuplot via `tsd.core.enable_ui = true` and remove the shell files https://github.com/OpenTSDB/opentsdb/blob/master/src/mygnuplot.bat and https://github.com/OpenTSDB/opentsdb/blob/master/src/mygnuplot.sh.

## References
- https://github.com/OpenTSDB/opentsdb/security/advisories/GHSA-76f7-9v52-v2fw
- https://nvd.nist.gov/vuln/detail/CVE-2023-36812
- https://github.com/OpenTSDB/opentsdb/commit/07c4641471c6f5c2ab5aab615969e97211eb50d9
- https://github.com/OpenTSDB/opentsdb/commit/fa88d3e4b5369f9fb73da384fab0b23e246309ba
- https://github.com/OpenTSDB/opentsdb
- http://packetstormsecurity.com/files/174570/OpenTSDB-2.4.1-Unauthenticated-Command-Injection.html
