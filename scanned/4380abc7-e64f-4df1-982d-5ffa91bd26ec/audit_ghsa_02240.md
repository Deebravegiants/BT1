# [C] OS Command Injection in OpenTSDB

## Summary
Severity: Critical
Advisory: GHSA-hv53-q76c-7f8c
CVE: CVE-2020-35476
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-hv53-q76c-7f8c
Type: github-advisory

## Affected
- Maven: `net.opentsdb:opentsdb` — affected >=0

## Details
A remote code execution vulnerability occurs in OpenTSDB through 2.4.0 via command injection in the yrange parameter. The yrange value is written to a gnuplot file in the /tmp directory. This file is then executed via the mygnuplot.sh shell script. (tsd/GraphHandler.java attempted to prevent command injections by blocking backticks but this is insufficient.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35476
- https://github.com/OpenTSDB/opentsdb/issues/2051
- http://packetstormsecurity.com/files/170331/OpenTSDB-2.4.0-Command-Injection.html
