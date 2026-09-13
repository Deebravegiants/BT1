# [M] Destroying OAuth Applications doesn't notify Streaming of Access Tokens being destroyed in mastodon

## Summary
Severity: Medium
Advisory: BIT-mastodon-2024-25619
Aliases: CVE-2024-25619, GHSA-7w3c-p9j8-mq3x
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-mastodon-2024-25619
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=0 <4.2.6

## Details
Mastodon is a free, open-source social network server based on ActivityPub. When an OAuth Application is destroyed, the streaming server wasn't being informed that the Access Tokens had also been destroyed, this could have posed security risks to users by allowing an application to continue listening to streaming after the application had been destroyed. Essentially this comes down to the fact that when Doorkeeper sets up the relationship between Applications and Access Tokens, it uses a `dependent: delete_all` configuration, which means the `after_commit` callback setup on `AccessTokenExtension` didn't actually fire, since `delete_all` doesn't trigger ActiveRecord callbacks. To mitigate, we need to add a `before_destroy` callback to `ApplicationExtension` which announces to streaming that all the Application's Access Tokens are being "killed". Impact should be negligible given the affected application had to be owned by the user. None the less this issue has been addressed in versions 4.2.6, 4.1.14, 4.0.14, and 3.5.18. Users are advised to upgrade. There are no known workaround for this vulnerability.

## References
- https://github.com/mastodon/mastodon/commit/68eaa804c9bafdc5f798e114e9ba00161425dd71
- https://github.com/mastodon/mastodon/security/advisories/GHSA-7w3c-p9j8-mq3x
- https://nvd.nist.gov/vuln/detail/CVE-2024-25619
