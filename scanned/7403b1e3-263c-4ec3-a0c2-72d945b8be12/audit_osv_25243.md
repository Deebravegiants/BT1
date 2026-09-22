# [M] Arbitrary file read in Ombi

## Summary
Severity: Medium
Advisory: CVE-2023-32322
Aliases: GHSA-28j3-84m7-gpjp
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-32322
Type: osv

## Details
Ombi is an open source application which allows users to request specific media from popular self-hosted streaming servers. Versions prior to 4.38.2 contain an arbitrary file read vulnerability where an Ombi administrative user may access files available to the Ombi server process on the host operating system. Ombi administrators may not always be local system administrators and so this may violate the security expectations of the system. The arbitrary file read vulnerability was present in `ReadLogFile` and `Download` endpoints in `SystemControllers.cs` as the parameter `logFileName` is not sanitized before being combined with the `Logs` directory. When using `Path.Combine(arg1, arg2, arg3)`, an attacker may be able to escape to folders/files outside of `Path.Combine(arg1, arg2)` by using ".." in `arg3`. In addition, by specifying an absolute path for `arg3`, `Path.Combine` will completely ignore the first two arguments and just return just `arg3`. This vulnerability can lead to information disclosure. The Ombi `documentation` suggests running Ombi as a Service with Administrator privileges. An attacker targeting such an application may be able to read the files of any Windows user on the host machine and certain system files. This issue has been addressed in commit `b8a8f029` and in release version 4.38.2. Users are advised to upgrade. There are no known workarounds for this vulnerability. This issue is also tracked as GHSL-2023-088.

## References
- https://docs.ombi.app/guides/installation/#windows
- https://github.com/Ombi-app/Ombi/blob/v4.36.1/src/Ombi/Controllers/V2/SystemController.cs#L46
- https://github.com/Ombi-app/Ombi/blob/v4.36.1/src/Ombi/Controllers/V2/SystemController.cs#L58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32322.json
- https://github.com/Ombi-app/Ombi/security/advisories/GHSA-28j3-84m7-gpjp
- https://nvd.nist.gov/vuln/detail/CVE-2023-32322
- https://github.com/Ombi-app/Ombi/commit/b8a8f029d80454d582bc4a2a05175106809335d0
