# [H] Apache Pulsar: Pulsar Functions Worker Allows Unauthorized File Access and Unauthorized HTTP/HTTPS Proxying

## Summary
Severity: High
Advisory: GHSA-c2x9-vw5h-39vc
CVE: CVE-2024-27894
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-12
Source: https://github.com/advisories/GHSA-c2x9-vw5h-39vc
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=2.4.0 <2.10.6
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=2.11.0 <2.11.4
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.0.0 <3.0.3
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.1.0 <3.1.3
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.2.0 <3.2.1

## Details
The Pulsar Functions Worker includes a capability that permits authenticated users to create functions where the function's implementation is referenced by a URL. The supported URL schemes include "file", "http", and "https". When a function is created using this method, the Functions Worker will retrieve the implementation from the URL provided by the user. However, this feature introduces a vulnerability that can be exploited by an attacker to gain unauthorized access to any file that the Pulsar Functions Worker process has permissions to read. This includes reading the process environment which potentially includes sensitive information, such as secrets. Furthermore, an attacker could leverage this vulnerability to use the Pulsar Functions Worker as a proxy to access the content of remote HTTP and HTTPS endpoint URLs. This could also be used to carry out denial of service attacks.
This vulnerability also applies to the Pulsar Broker when it is configured with "functionsWorkerEnabled=true".

This issue affects Apache Pulsar versions from 2.4.0 to 2.10.5, from 2.11.0 to 2.11.3, from 3.0.0 to 3.0.2, from 3.1.0 to 3.1.2, and 3.2.0. 

2.10 Pulsar Function Worker users should upgrade to at least 2.10.6.
2.11 Pulsar Function Worker users should upgrade to at least 2.11.4.
3.0 Pulsar Function Worker users should upgrade to at least 3.0.3.
3.1 Pulsar Function Worker users should upgrade to at least 3.1.3.
3.2 Pulsar Function Worker users should upgrade to at least 3.2.1.

Users operating versions prior to those listed above should upgrade to the aforementioned patched versions or newer versions.

The updated versions of Pulsar Functions Worker will, by default, impose restrictions on the creation of functions using URLs. For users who rely on this functionality, the Function Worker configuration provides two configuration keys: "additionalEnabledConnectorUrlPatterns" and "additionalEnabledFunctionsUrlPatterns". These keys allow users to specify a set of URL patterns that are permitted, enabling the creation of functions using URLs that match the defined patterns. This approach ensures that the feature remains available to those who require it, while limiting the potential for unauthorized access and exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27894
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/45cqhgqg8d19ongjw18ypcss8vwh206p
- https://pulsar.apache.org/security/CVE-2024-27894
- http://www.openwall.com/lists/oss-security/2024/03/12/11
