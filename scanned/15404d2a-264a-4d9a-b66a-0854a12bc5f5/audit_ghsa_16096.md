# [M] Missing ratelimit on passwrod resets in zenml

## Summary
Severity: Medium
Advisory: GHSA-j3vq-pmp5-r5xj
CVE: CVE-2024-4311
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2024-11-14
Source: https://github.com/advisories/GHSA-j3vq-pmp5-r5xj
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.57.0rc2

## Details
zenml-io/zenml version 0.56.4 is vulnerable to an account takeover due to the lack of rate-limiting in the password change function. An attacker can brute-force the current password in the 'Update Password' function, allowing them to take over the user's account. This vulnerability is due to the absence of rate-limiting on the '/api/v1/current-user' endpoint, which does not restrict the number of attempts an attacker can make to guess the current password. Successful exploitation results in the attacker being able to change the password and take control of the account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4311
- https://github.com/zenml-io/zenml/commit/87a6c2c8f45b49ea83fbb5fe8fff7ab5365a60c9
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/d5517e1a-6b94-4e38-aad6-3aa65f98bec2
