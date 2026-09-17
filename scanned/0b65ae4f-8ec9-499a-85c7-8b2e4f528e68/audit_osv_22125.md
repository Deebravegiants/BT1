# [M] Privileged Escalation in Istio

## Summary
Severity: Medium
Advisory: CVE-2022-21701
Aliases: GHSA-mq8f-9446-c28r
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/CVE-2022-21701
Type: osv

## Details
Istio is an open platform to connect, manage, and secure microservices. In versions 1.12.0 and 1.12.1 Istio is vulnerable to a privilege escalation attack. Users who have `CREATE` permission for `gateways.gateway.networking.k8s.io` objects can escalate this privilege to create other resources that they may not have access to, such as `Pod`. This vulnerability impacts only an Alpha level feature, the Kubernetes Gateway API. This is not the same as the Istio Gateway type (gateways.networking.istio.io), which is not vulnerable. Users are advised to upgrade to resolve this issue. Users unable to upgrade should implement any of the following which will prevent this vulnerability: Remove the gateways.gateway.networking.k8s.io CustomResourceDefinition, set PILOT_ENABLE_GATEWAY_API_DEPLOYMENT_CONTROLLER=true environment variable in Istiod, or remove CREATE permissions for gateways.gateway.networking.k8s.io objects from untrusted users.

## References
- https://istio.io/latest/news/releases/1.12.x/announcing-1.12.2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21701.json
- https://github.com/istio/istio/security/advisories/GHSA-mq8f-9446-c28r
- https://nvd.nist.gov/vuln/detail/CVE-2022-21701
