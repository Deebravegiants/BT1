# [H] CVE-2026-76403

## Summary
Severity: High
Advisory: CVE-2026-76403
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76403
Type: osv

## Details
In Splunk Connect for Kafka versions below 2.2.7, an unauthenticated user positioned in the network path could read or alter all relevant data sent from the connector when Kerberos authentication is used with Hypertext Transfer Protocol (HTTP) Event Collector in Splunk Enterprise. The vulnerability is possible because the Kerberos authentication path does not apply the configured certificate validation options when it builds the HTTP client. For more information see Install Splunk Connect for Kafka (https://help.splunk.com/en/data-management/integrate-data-with-add-ons/splunk-connect-for-kafka/2.2/install/install-splunk-connect-for-kafka), Security configurations for Splunk Connect for Kafka (https://help.splunk.com/en/splunk-enterprise/get-data-in/splunk-connect-for-kafka/2.2/configure/security-configurations-for-splunk-connect-for-kafka), and Set up and use HTTP Event Collector with configuration files (https://help.splunk.com/en/splunk-enterprise/get-data-in/get-started-with-getting-data-in/9.4/get-data-with-http-event-collector/set-up-and-use-http-event-collector-with-configuration-files) in the Splunk documentation.

## References
- https://advisory.splunk.com/advisories/SVD-2026-0808
