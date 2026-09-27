# [M] Home Assistant vulnerable to account takeover via auth_callback login

## Summary
Severity: Medium
Advisory: GHSA-qhhj-7hrc-gqj5
CVE: CVE-2023-41893
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-qhhj-7hrc-gqj5
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2023.9.0

## Details
[_Part of the Cure53 security audit of Home Assistant._](https://www.home-assistant.io/blog/2023/10/19/security-audits-of-home-assistant/)

The audit team’s analyses confirmed that the `redirect_uri` and `client_id` are alterable when logging in. Consequently, the code parameter utilized to fetch the `access_token` post-authentication will be sent to the URL specified in the aforementioned parameters.

Since an arbitrary URL is permitted and `homeassistant.local` represents the preferred, default domain likely used and trusted by many users, an attacker could leverage this weakness to manipulate a user and retrieve account access. Notably, this attack strategy is plausible if the victim has exposed their Home Assistant to the Internet, since after acquiring the victim’s `access_token`, the adversary would need to utilize it directly towards the instance to achieve any pertinent malicious actions.

To achieve this compromise attempt, the attacker must send a link with a `redirect_uri` that they control to the victim’s own Home Assistant instance. In the eventuality the victim authenticates via the said link, the attacker would obtain code sent to the specified URL in `redirect_uri`, which can then be leveraged to fetch an `access_token`.

An attacker could increase the efficacy of this strategy by registering a nearly identical domain to `homeassistant.local`, which at first glance may appear legitimate and thereby obfuscate any malicious intentions.

Nonetheless, owing to the requirements for victim interaction and Home Assistant instance exposure to the Internet, this severity rating was consequently downgraded to Low.

## References
- https://github.com/home-assistant/core/security/advisories/GHSA-qhhj-7hrc-gqj5
- https://nvd.nist.gov/vuln/detail/CVE-2023-41893
- https://github.com/home-assistant/core
- https://github.com/pypa/advisory-database/tree/main/vulns/homeassistant/PYSEC-2023-214.yaml
- https://www.home-assistant.io/blog/2023/10/19/security-audits-of-home-assistant
