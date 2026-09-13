# [C] Integrated Scripting vulnerable to arbitrary code execution via Java reflection

## Summary
Severity: Critical
Advisory: CVE-2025-27107
Aliases: GHSA-2v5x-4823-hq77
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-03-13
Source: https://osv.dev/vulnerability/CVE-2025-27107
Type: osv

## Details
Integrated Scripting is a tool for creating scripts for handling complex operations in Integrated Dynamics. Minecraft users who use Integrated Scripting prior to versions 1.21.1-1.0.17, 1.21.4-1.0.9-254, 1.20.1-1.0.13, and 1.19.2-1.0.10 may be vulnerable to arbitrary code execution. By using Java reflection on a thrown exception object it's possible to escape the JavaScript sandbox for IntegratedScripting's Variable Cards, and leverage that to construct arbitrary Java classes and invoke arbitrary Java methods.
This vulnerability allows for execution of arbitrary Java methods, and by extension arbitrary native code e.g. from `java.lang.Runtime.exec`, on the Minecraft server by any player with the ability to create and use an IntegratedScripting Variable Card. Versions 1.21.1-1.0.17, 1.21.4-1.0.9-254, 1.20.1-1.0.13, and 1.19.2-1.0.10 fix the issue.

## References
- https://github.com/CyclopsMC/IntegratedScripting/blob/29051aace619604fb5dd60624b72dba428fea2f2/src/main/java/org/cyclops/integratedscripting/evaluate/ScriptHelpers.java#L46
- https://github.com/CyclopsMC/IntegratedScripting/blob/29051aace619604fb5dd60624b72dba428fea2f2/src/main/java/org/cyclops/integratedscripting/evaluate/translation/ValueTranslators.java
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27107.json
- https://github.com/CyclopsMC/IntegratedScripting/security/advisories/GHSA-2v5x-4823-hq77
- https://nvd.nist.gov/vuln/detail/CVE-2025-27107
