# [C] Clojure classes can be used to craft a serialized object that runs arbitrary code on deserialization

## Summary
Severity: Critical
Advisory: GHSA-jgxc-8mwq-9xqw
CVE: CVE-2017-20189
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-jgxc-8mwq-9xqw
Type: github-advisory

## Affected
- Maven: `org.clojure:clojure` — affected >=0 <1.9.0

## Details
In Clojure before 1.9.0, classes can be used to construct a serialized object that executes arbitrary code upon deserialization. This is relevant if a server deserializes untrusted objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20189
- https://github.com/frohoff/ysoserial/pull/68/files
- https://github.com/clojure/clojure/commit/271674c9b484d798484d134a5ac40a6df15d3ac3
- https://clojure.atlassian.net/browse/CLJ-2204
- https://github.com/clojure/clojure
- https://groups.google.com/d/msg/clojure/WaL3hHzsevI/7zHU-L7LBQAJ
- https://hackmd.io/%40fe1w0/HyefvRQKp
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://security.snyk.io/vuln/SNYK-JAVA-ORGCLOJURE-5740378
