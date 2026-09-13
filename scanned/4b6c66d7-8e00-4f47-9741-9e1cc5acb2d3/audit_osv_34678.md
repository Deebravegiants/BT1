# [C] CVE-2025-63690

## Summary
Severity: Critical
Advisory: CVE-2025-63690
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-63690
Type: osv

## Details
In pig-mesh Pig versions 3.8.2 and below, when setting up scheduled tasks in the Quartz management function under the system management module, it is possible to execute any Java class with a parameterless constructor and its methods with parameter type String through reflection. At this time, the eval method in Tomcat's built-in class jakarta.el.ELProcessor can be used to execute commands, leading to a remote code execution vulnerability.

## References
- https://github.com/LockeTom/vulnerability/blob/main/md/pig_Remote_Code_Execution_Vulnerability.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63690.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63690
- https://github.com/pig-mesh/pig/issues/1199
