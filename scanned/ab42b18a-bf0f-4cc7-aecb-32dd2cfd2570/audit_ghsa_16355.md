# [M] Apache Ozone Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6726-2rx3-cgwh
CVE: CVE-2023-39196
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-6726-2rx3-cgwh
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=1.2.0 <1.4.0

## Details
Improper Authentication vulnerability in Apache Ozone.

The vulnerability allows an attacker to download metadata internal to the Storage Container Manager service without proper authentication.
The attacker is not allowed to do any modification within the Ozone Storage Container Manager service using this vulnerability.
The accessible metadata does not contain sensitive information that can be used to exploit the system later on, and the accessible data does not make it possible to gain access to actual user data within Ozone.
This issue affects Apache Ozone: 1.2.0 and subsequent releases up until 1.3.0.

Users are recommended to upgrade to version 1.4.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39196
- https://github.com/apache/ozone
- https://lists.apache.org/thread/o96ct5t7kj5cgrmmfc6756m931t08nky
- http://www.openwall.com/lists/oss-security/2024/02/07/2
