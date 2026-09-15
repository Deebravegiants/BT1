# [M] Instrumentation for AWS SDK v2 captures email content when using Amazon Simple Email Service (SES) v1 API, exposing that content to the telemetry backend

## Summary
Severity: Medium
Advisory: CVE-2023-39951
Aliases: GHSA-hghr-r469-gfq6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-08
Source: https://osv.dev/vulnerability/CVE-2023-39951
Type: osv

## Details
OpenTelemetry Java Instrumentation provides OpenTelemetry auto-instrumentation and instrumentation libraries for Java. OpenTelemetry Java Instrumentation prior to version 1.28.0 contains an issue related to the instrumentation of Java applications using the AWS SDK v2 with Amazon Simple Email Service (SES) v1 API. When SES POST requests are instrumented, the query parameters of the request are inserted into the trace `url.path` field. This behavior leads to the http body, containing the email subject and message, to be present in the trace request url metadata. Any user using a version before 1.28.0 of OpenTelemetry Java Instrumentation to instrument AWS SDK v2 call to SES’s v1 SendEmail API is affected. The e-mail content sent to SES may end up in telemetry backend. This exposes the e-mail content to unintended audiences. The issue can be mitigated by updating OpenTelemetry Java Instrumentation to version 1.28.0 or later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39951.json
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/security/advisories/GHSA-hghr-r469-gfq6
- https://nvd.nist.gov/vuln/detail/CVE-2023-39951
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/issues/8956
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/pull/8931
