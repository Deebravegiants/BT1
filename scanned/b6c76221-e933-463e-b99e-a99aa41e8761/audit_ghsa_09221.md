# [M] Spring Cloud AWS missing SNS message signature verification allows spoofing of HTTP/HTTPS endpoint notifications

## Summary
Severity: Medium
Advisory: GHSA-r4w4-wv68-qv85
CVE: CVE-2026-44308
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-r4w4-wv68-qv85
Type: github-advisory

## Affected
- Maven: `io.awspring.cloud:spring-cloud-aws-sns` — affected >=4.0.0 <4.0.2
- Maven: `io.awspring.cloud:spring-cloud-aws-sns` — affected >=3.0.0

## Details
### Impact
  
  Applications using Spring Cloud AWS SNS HTTP/HTTPS endpoint support (@NotificationMessageMapping, @NotificationSubscriptionMapping, @NotificationUnsubscribeConfirmationMapping) did not verify the signature of incoming SNS messages.

An unauthenticated attacker who knows the endpoint URL could send crafted HTTP POST requests mimicking SNS Notification or SubscriptionConfirmation messages, causing the application to:
  
  - Process arbitrary payloads as if they were legitimate SNS notifications.
  - Auto-confirm subscriptions or unsubscribe from attacker-controlled topics.
  
Affected versions: 3.0.0 through 3.4.2, 4.0.0, and 4.0.1.
  
The 3.x line will not receive a fix; users on 3.x should apply the workaround below or upgrade to 4.0.2.
  
### Patches
  
Fixed in Spring Cloud AWS 4.0.2. When using Spring Boot auto-configuration, signature verification is enabled by default. Users should upgrade to 4.0.2.
  
### Workarounds
  
Manually verify the SNS message signature in a servlet filter or Spring HandlerInterceptor before the request reaches the controller, using SnsMessageManager from the AWS SDK v2 sns-message-manager module.
  
 ### Resources
  
  - AWS SNS: Verifying the signatures of Amazon SNS messages (https://docs.aws.amazon.com/sns/latest/dg/sns-verify-signature-of-message.html)
  - AWS SDK for Java v2: SnsMessageManager (https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/messagemanager/sns/SnsMessageManager.html)
  - Fix PR: #1614

## References
- https://github.com/awspring/spring-cloud-aws/security/advisories/GHSA-r4w4-wv68-qv85
- https://nvd.nist.gov/vuln/detail/CVE-2026-44308
- https://github.com/awspring/spring-cloud-aws/pull/1614
- https://github.com/awspring/spring-cloud-aws/commit/6ab2efd97891a3d0ed0126ffa1ce223c9cfa9638
- https://github.com/awspring/spring-cloud-aws
