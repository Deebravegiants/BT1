# [M] Google Play Services SDK leads to apps having incorrectly set mutability flag

## Summary
Severity: Medium
Advisory: GHSA-cm6r-892j-jv2g
CVE: CVE-2022-2390
CWE: CWE-471
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-08-13
Source: https://github.com/advisories/GHSA-cm6r-892j-jv2g
Type: github-advisory

## Affected
- Maven: `com.google.android.gms:play-services-basement` — affected >=0 <18.0.2

## Details
Apps developed with Google Play Services SDK incorrectly had the mutability flag set to PendingIntents that were passed to the Notification service. As Google Play services SDK is so widely used, this bug affects many applications. For an application affected, this bug will let the attacker, gain the access to all non-exported providers and/or gain the access to other providers the victim has permissions. We recommend upgrading to version 18.0.2 of the Play Service SDK as well as rebuilding and redeploying apps.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2390
- https://developers.google.com/android/guides/releases#may_03_2022
- https://mvnrepository.com/artifact/com.google.android.gms/play-services-basement/18.0.2
