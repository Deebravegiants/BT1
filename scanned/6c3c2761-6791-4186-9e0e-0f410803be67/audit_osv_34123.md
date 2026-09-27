# [M] Apache Spark, Apache Spark: RPC encryption defaults to unauthenticated AES-CTR mode, enabling man-in-the-middle ciphertext modification attacks

## Summary
Severity: Medium
Advisory: CVE-2025-55039
Aliases: GHSA-6p6v-m64v-jx8q, PYSEC-2025-184
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-55039
Type: osv

## Details
This issue affects Apache Spark versions before  3.4.4, 3.5.2 and 4.0.0.



Apache Spark versions before 4.0.0, 3.5.2 and 3.4.4 use an insecure default network encryption cipher for RPC communication between nodes.

When spark.network.crypto.enabled is set to true (it is set to false by default), but spark.network.crypto.cipher is not explicitly configured, Spark defaults to AES in CTR mode (AES/CTR/NoPadding), which provides encryption without authentication.

This vulnerability allows a man-in-the-middle attacker to modify encrypted RPC traffic undetected by flipping bits in ciphertext, potentially compromising heartbeat messages or application data and affecting the integrity of Spark workflows.


To mitigate this issue, users should either configure spark.network.crypto.cipher to AES/GCM/NoPadding to enable authenticated encryption or

enable SSL encryption by setting spark.ssl.enabled to true, which provides stronger transport security.

## References
- http://www.openwall.com/lists/oss-security/2025/10/14/11
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55039.json
- https://lists.apache.org/thread/zrgyy9l85nm2c7vk36vr7bkyorg3w4qq
- https://nvd.nist.gov/vuln/detail/CVE-2025-55039
