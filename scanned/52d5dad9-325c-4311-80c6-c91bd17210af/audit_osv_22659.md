# [H] Crafted link in Zulip message can cause disclosure of credentials

## Summary
Severity: High
Advisory: CVE-2022-35962
Aliases: GHSA-4gj2-j32x-4wg5
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-35962
Type: osv

## Details
Zulip is an open source team chat and Zulip Mobile is an app for iOS and Andriod users. In Zulip Mobile through version 27.189, a crafted link in a message sent by an authenticated user could lead to credential disclosure if a user follows the link. A patch was released in version 27.190.

## References
- https://github.com/zulip/zulip-mobile/releases/tag/v27.190
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35962.json
- https://github.com/zulip/zulip-mobile/security/advisories/GHSA-4gj2-j32x-4wg5
- https://nvd.nist.gov/vuln/detail/CVE-2022-35962
- https://blog.zulip.com/2022/08/24/zulip-server-5-6-security-release/
