# [H] CVE-2017-12161

## Summary
Severity: High
Advisory: CVE-2017-12161
Aliases: GHSA-959q-32g8-vvp7
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-21
Source: https://osv.dev/vulnerability/CVE-2017-12161
Type: osv

## Details
It was found that keycloak before 3.4.2 final would permit misuse of a client-side /etc/hosts entry to spoof a URL in a password reset request. An attacker could use this flaw to craft a malicious password reset request and gain a valid reset token, leading to information disclosure or further attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1484564
- https://github.com/keycloak/keycloak-documentation/pull/268/commits/a2b58aadee42af2c375b72e86dffc2cf23cc3770
