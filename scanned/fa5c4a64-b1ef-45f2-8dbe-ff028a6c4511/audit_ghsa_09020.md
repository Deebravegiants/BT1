# [C] Apache MINA vulnerable to Deserialization of Untrusted Data (CVE-2026-41635 Incomplete Fix)

## Summary
Severity: Critical
Advisory: GHSA-vf5j-865m-mq7c
CVE: CVE-2026-42779
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-vf5j-865m-mq7c
Type: github-advisory

## Affected
- Maven: `org.apache.mina:mina-core` — affected >=2.1.0 <2.1.12
- Maven: `org.apache.mina:mina-core` — affected >=2.2.0 <2.2.7

## Details
The fix for CVE-2026-41635 was not applied to the 2.1.X and 2.2.X branches. Here was the original issue description:

Apache MINA's AbstractIoBuffer.resolveClass() contains two branches, one of them (for static classes or primitive types) does not check the class at all, bypassing the classname allowlist and allowing arbitrary code to be executed.

The fix checks if the class is present in the accepted class filter before calling Class.forName(). 

Affected versions are Apache MINA 2.1.0 <= 2.1.11, and 2.2.0 <= 2.2.6.

The problem is resolved in Apache MINA 2.1.12, and 2.2.7 by applying the classname allowlist earlier.

Affected are applications using Apache MINA that call  IoBuffer.getObject().

Applications using Apache MINA are advised to upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42779
- https://github.com/advisories/GHSA-8297-v2rf-2p32
- https://github.com/apache/mina
- https://lists.apache.org/thread/fhlx5k91hrkgyzh7yk1nghrn3k27gxy0
