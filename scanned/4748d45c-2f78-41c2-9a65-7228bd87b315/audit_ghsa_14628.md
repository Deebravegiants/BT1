# [H] Apache Ozone: Improper authentication when generating S3 secrets

## Summary
Severity: High
Advisory: GHSA-rcq8-9q3j-98mw
CVE: CVE-2024-45106
CWE: CWE-287, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-rcq8-9q3j-98mw
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone` — affected >=1.4.0 <1.4.1

## Details
Improper authentication of an HTTP endpoint in the S3 Gateway of Apache Ozone 1.4.0 allows any authenticated Kerberos user to revoke and regenerate the S3 secrets of any other user. This is only possible if:
  *  ozone.s3g.secret.http.enabled is set to true. The default value of this configuration is false.
  *  The user configured in ozone.s3g.kerberos.principal is also configured in ozone.s3.administrators or ozone.administrators.


Users are recommended to upgrade to Apache Ozone version 1.4.1 which disables the affected endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45106
- https://github.com/apache/ozone/pull/5233
- https://github.com/apache/ozone
- https://lists.apache.org/thread/rylnxwttp004kvotpk9j158vb238pfkm
- http://www.openwall.com/lists/oss-security/2024/12/02/1
