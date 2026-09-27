# [M] Sentry vulnerable to invite code reuse via cookie manipulation

## Summary
Severity: Medium
Advisory: GHSA-jv85-mqxj-3f9j
CVE: CVE-2022-23485
CWE: CWE-269, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-jv85-mqxj-3f9j
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=20.6.0 <22.11.0

## Details
With a known valid invite link (i.e. not already accepted or expired) an unauthenticated attacker can manipulate the cookie to allow the same invite link to be reused on multiple accounts when joining an organization.

### Impact
An attacker with a valid invite link can create multiple users and join the organization from which the invite link was generated.

### Patches
This issue was patched in version 22.11.0.

### Workarounds
Sentry SaaS customers do not need to take action.

Self-hosted Sentry installs can disable the invite functionality until they are ready to deploy the patched version by editing their `sentry.conf.py` file (usually located at `~/.sentry/`).

1. Add the following line into `sentry.conf.py`:

    ```python
     SENTRY_FEATURES["organizations:invite-members"] = False
    ```
2. Restart the Sentry web service.

    ```
    docker compose restart web
    ```

### For more information
If you have any questions or comments about this advisory:
* [Visit our FAQs on this CVE](https://help.sentry.io/account/security/cve-2022-23485-faqs/)
* Open an issue in [getsentry/sentry](http://github.com/getsentry/sentry)
* Email us at security[@]sentry.io

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-jv85-mqxj-3f9j
- https://nvd.nist.gov/vuln/detail/CVE-2022-23485
- https://github.com/getsentry/sentry/commit/565f971da955d57c754a47f5802fe9f9f7c66b39
- https://github.com/getsentry/sentry
- https://github.com/pypa/advisory-database/tree/main/vulns/sentry/PYSEC-2022-43011.yaml
