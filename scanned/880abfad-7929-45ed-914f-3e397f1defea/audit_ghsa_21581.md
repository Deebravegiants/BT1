# [M] Lack of authentication mechanism for webhook in CloudBees Docker Hub/Registry Notification Plugin

## Summary
Severity: Medium
Advisory: GHSA-v535-pc6r-77qh
CVE: CVE-2022-45385
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-v535-pc6r-77qh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dockerhub-notification` — affected >=0 <2.6.2.1

## Details
CloudBees Docker Hub/Registry Notification Plugin provides several webhook endpoints that can be used to trigger builds when Docker images used by a job have been rebuilt.

In CloudBees Docker Hub/Registry Notification Plugin 2.6.2 and earlier, these endpoints can be accessed without authentication.

This allows unauthenticated attackers to trigger builds of jobs corresponding to the attacker-specified repository.

CloudBees Docker Hub/Registry Notification Plugin 2.6.2.1 requires a token as a part of webhook URLs, which will act as authentication for the webhook endpoint. As a result, all webhook URLs in the plugin will be different after updating the plugin.

Administrators can set the [Java system](https://www.jenkins.io/doc/book/managing/system-properties/) property `org.jenkinsci.plugins.registry.notification.webhook.JSONWebHook.DO_NOT_REQUIRE_API_TOKEN` to `true` to disable this fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45385
- https://github.com/jenkinsci/dockerhub-notification-plugin/commit/1163d4f297af23266c032fc66bd603b97f9ecd4b
- https://github.com/jenkinsci/dockerhub-notification-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2843
- http://www.openwall.com/lists/oss-security/2022/11/15/4
