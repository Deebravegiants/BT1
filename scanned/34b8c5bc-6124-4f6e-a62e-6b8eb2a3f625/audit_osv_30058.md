# [H] Unsafe Reflection in base Component class in yiisoft/yii2

## Summary
Severity: High
Advisory: CVE-2024-4990
Aliases: GHSA-cjcc-p67m-7qxm
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-4990
Type: osv

## Details
In yiisoft/yii2 version 2.0.48, the base Component class contains a vulnerability where the `__set()` magic method does not validate that the value passed is a valid Behavior class name or configuration. This allows an attacker to instantiate arbitrary classes, passing parameters to their constructors and invoking setter methods. Depending on the installed dependencies, various types of attacks are possible, including the execution of arbitrary code, retrieval of sensitive information, and unauthorized access.

## References
- https://huntr.com/bounties/4fbdd965-02b6-42e4-b57b-f98f93415b8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4990.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4990
