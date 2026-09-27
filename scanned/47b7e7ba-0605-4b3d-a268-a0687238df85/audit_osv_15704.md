# [C] CVE-2019-18933

## Summary
Severity: Critical
Advisory: CVE-2019-18933
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-18933
Type: osv

## Details
In Zulip Server versions from 1.7.0 to before 2.0.7, a bug in the new user signup process meant that users who registered their account using social authentication (e.g., GitHub or Google SSO) in an organization that also allows password authentication could have their personal API key stolen by an unprivileged attacker, allowing nearly full access to the user's account.

## References
- https://blog.zulip.org/2019/11/21/zulip-2-0-7-security-release/
- https://github.com/zulip/zulip/commit/0c2cc41d2e40807baa5ee2c72987ebfb64ea2eb6
