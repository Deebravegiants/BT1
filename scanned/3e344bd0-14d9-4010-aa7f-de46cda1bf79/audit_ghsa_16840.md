# [M] Apache Solr Operator liveness and readiness probes may leak basic auth credentials

## Summary
Severity: Medium
Advisory: GHSA-g9qx-25vj-rf53
CVE: CVE-2024-31391
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-g9qx-25vj-rf53
Type: github-advisory

## Affected
- Go: `github.com/apache/solr-operator` — affected >=0.3.0 <0.8.1

## Details
Insertion of Sensitive Information into Log File vulnerability in the Apache Solr Operator.

This issue affects all versions of the Apache Solr Operator from 0.3.0 through 0.8.0.

When asked to bootstrap Solr security, the operator will enable basic authentication and create several accounts for accessing Solr: including the "solr" and "admin" accounts for use by end-users, and a "k8s-oper" account which the operator uses for its own requests to Solr.
One common source of these operator requests is healthchecks: liveness, readiness, and startup probes are all used to determine Solr's health and ability to receive traffic.
By default, the operator configures the Solr APIs used for these probes to be exempt from authentication, but users may specifically request that authentication be required on probe endpoints as well.
Whenever one of these probes would fail, if authentication was in use, the Solr Operator would create a Kubernetes "event" containing the username and password of the "k8s-oper" account.

Within the affected version range, this vulnerability affects any solrcloud resource which (1) bootstrapped security through use of the `.solrOptions.security.authenticationType=basic` option, and (2) required authentication be used on probes by setting `.solrOptions.security.probesRequireAuth=true`.

Users are recommended to upgrade to Solr Operator version 0.8.1, which fixes this issue by ensuring that probes no longer print the credentials used for Solr requests.  Users may also mitigate the vulnerability by disabling authentication on their healthcheck probes using the setting `.solrOptions.security.probesRequireAuth=false`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31391
- https://github.com/apache/solr-operator
- https://lists.apache.org/thread/w7011s78lzywzwyszvy4d8zm99ybt8c7
- http://www.openwall.com/lists/oss-security/2024/04/12/7
