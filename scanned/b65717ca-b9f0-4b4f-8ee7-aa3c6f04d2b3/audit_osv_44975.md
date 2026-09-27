# [C] uproot 5.7.4 and prior Code Injection via TStreamerInfo Metadata

## Summary
Severity: Critical
Advisory: CVE-2026-9147
Aliases: GHSA-6946-mq52-g438
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-9147
Type: osv

## Details
uproot dynamically generates Python class source code from ROOT TStreamerInfo records in a file and compiles it at runtime. Some file-controlled streamer metadata fields (for example, streamer element names) are interpolated into the generated Python source without safe quoting via repr() or the !r format specifier. An attacker who can supply a crafted ROOT file can place Python expression-breaking content into a streamer metadata field. When uproot generates and invokes the corresponding reader method, the injected Python expression is evaluated in the context of the process opening the file, resulting in arbitrary Python code execution in applications that open or process attacker-controlled ROOT files with affected uproot code paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9147.json
- https://github.com/scikit-hep/uproot5/security/advisories/GHSA-6946-mq52-g438
- https://nvd.nist.gov/vuln/detail/CVE-2026-9147
- https://www.vulncheck.com/advisories/uproot-and-before-code-injection-via-tstreamerinfo-metadata
- https://github.com/scikit-hep/uproot5/commit/c045c2824295d907d2e705f31110c742928e50e7
- https://github.com/scikit-hep/uproot5
- https://github.com/SaiTeja-Erukude/CVE-2026-9147-uproot-rce
