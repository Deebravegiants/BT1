# [M] Improper Validation of Integrity Check Value in Bouncy Castle

## Summary
Severity: Medium
Advisory: GHSA-8477-3v39-ggpm
CVE: CVE-2018-5382
CWE: CWE-354
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8477-3v39-ggpm
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.50

## Details
The default BKS keystore use an HMAC that is only 16 bits long, which can allow an attacker to compromise the integrity of a BKS keystore. Bouncy Castle release 1.47 changes the BKS format to a format which uses a 160 bit HMAC instead. This applies to any BKS keystore generated prior to BC 1.47. For situations where people need to create the files for legacy reasons a specific keystore type "BKS-V1" was introduced in 1.49. It should be noted that the use of "BKS-V1" is discouraged by the library authors and should only be used where it is otherwise safe to do so, as in where the use of a 16 bit checksum for the file integrity check is not going to cause a security issue in itself.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5382
- https://access.redhat.com/errata/RHSA-2018:2927
- https://www.bouncycastle.org/releasenotes.html
- https://www.kb.cert.org/vuls/id/306792
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://www.securityfocus.com/bid/103453
