# [H] Nautobot's BANNER_* configuration can be used to inject arbitrary HTML content into Nautobot pages

## Summary
Severity: High
Advisory: GHSA-r2hr-4v48-fjv3
CVE: CVE-2024-34707
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-r2hr-4v48-fjv3
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=0 <1.6.22
- PyPI: `nautobot` — affected >=2.0.0 <2.2.4

## Details
### Impact

A Nautobot user with admin privileges can modify the `BANNER_TOP`, `BANNER_BOTTOM`, and `BANNER_LOGIN` configuration settings via the `/admin/constance/config/` endpoint. Normally these settings are used to provide custom banner text at the top and bottom of all Nautobot web pages (or specifically on the login page in the case of `BANNER_LOGIN`) but it was reported that an admin user can make use of these settings to inject arbitrary HTML, potentially exposing Nautobot users to security issues such as cross-site scripting (stored XSS).

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Patches will be released as part of Nautobot 1.6.22 and 2.2.4.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

As [described in the Nautobot documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/configuration/optional-settings/#administratively-configurable-settings), these settings are only configurable through the admin UI of Nautobot if they are *not* explicitly set to some non-empty value in the `nautobot_config.py` or equivalent Nautobot configuration file. Therefore, adding the following configuration to said file completely mitigates this vulnerability in both Nautobot 1.x and 2.x:

```python
BANNER_LOGIN = " "
BANNER_TOP = " "
BANNER_BOTTOM = " "
```

or alternately (Nautobot 2.x only), if those variables are not defined explicitly in your configuration file, setting the following environment variables for the Nautobot user account serves the same purpose:

```shell
NAUTOBOT_BANNER_LOGIN=" "
NAUTOBOT_BANNER_TOP=" "
NAUTOBOT_BANNER_BOTTOM=" "
```

Limiting all users who do not need elevated privileges to non-admin access (`is_superuser: False` and `is_staff: False`) is a partial mitigation as well.


### References

- https://github.com/nautobot/nautobot/pull/5697
- https://github.com/nautobot/nautobot/pull/5698

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-r2hr-4v48-fjv3
- https://nvd.nist.gov/vuln/detail/CVE-2024-34707
- https://github.com/nautobot/nautobot/pull/5697
- https://github.com/nautobot/nautobot/pull/5698
- https://github.com/nautobot/nautobot/commit/4f0a66bd6307bfe0e0acb899233e0d4ad516f51c
- https://github.com/nautobot/nautobot/commit/f640aedc69c848d3d1be57f0300fc40033ff6423
- https://github.com/nautobot/nautobot
