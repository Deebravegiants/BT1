# [C] Apache MINA: CWE-502 Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: CVE-2026-41409
Aliases: GHSA-f2wh-grmh-r6jm
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-41409
Type: osv

## Details
The fix for CVE-2024-52046 in Apache MINA AbstractIoBuffer.getObject() was incomplete. The classname allowlist of classes allowed to be deserialized was applied too late after a static initializer in a class to be read might already have been executed.




Affected versions are Apache MINA 2.0.0 <= 2.0.27, 2.1.0 <= 2.1.10, and 2.2.0 <= 2.2.5.




The problem is resolved in Apache MINA 2.0.28, 2.1.11, and 2.2.6 by 
applying the classname allowlist earlier.




Affected are applications using Apache MINA that call IoBuffer.getObject().




Applications using Apache MINA are advised to upgrade

## References
- https://repo.maven.apache.org/maven2/org/apache/mina/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41409.json
- https://lists.apache.org/thread/9ddvsq6c4l5bhwq8l14sob4f8qjvx5c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41409
