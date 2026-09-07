# [C] Security Advisory for "Log4Shell"

## Summary
Severity: Critical
Advisory: GHSA-v57x-gxfj-484q
CWE: CWE-20, CWE-400, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-v57x-gxfj-484q
Type: github-advisory

## Affected
- Maven: `com.hazelcast.jet:hazelcast-jet` — affected >=4.1 <4.5.3
- Maven: `com.hazelcast:hazelcast` — affected >=5.0 <5.0.2
- Maven: `com.hazelcast:hazelcast` — affected >=4.0.0 <4.0.5
- Maven: `com.hazelcast:hazelcast` — affected >=4.1.1 <4.1.8
- Maven: `com.hazelcast:hazelcast` — affected >=4.2 <4.2.4

## Details
### Impact
A highly critical 0-day exploit (CVE-2021-44228) is found in Apache log4j 2 library on December 9, 2021.

This affects Apache log4j versions from 2.0-beta9 to 2.14.1 (inclusive). 

This vulnerability allows a remote attacker to execute code on the server if the system logs an attacker-controlled string value with the attacker's JNDI LDAP server lookup.

Another vulnerability related to the same library, which was discovered on 12/14/2021 (CVE-2021-45046) and revealed another Remote Code Execution vulnerability, has been investigated by Hazelcast team as well and it is found that it does not affect Hazelcast Products under default configurations. 

The finding of CVE-2021-45105 on 12/14/2021, which can cause a Denial of Service attack, was investigated by Hazelcast team and it is confirmed that it does not affect Hazelcast Products under default configurations. 

The finding of CVE-2021-44832 on 12/28/2021, which is a medium vulnerability, is investigated by our security team as well, and not considered to be as critical. It requires attacker to be able to modify logging configuration, which means attacker can modify the filesystem and/or can already execute arbitrary code which is more of a general security breach rather than something log4j specific.

Note that Hazelcast IMDG and IMDG Enterprise itself is not affected.

However, given version distributions are considered to be vulnerable since related ZIP and TGZ distributions contain a vulnerable Hazelcast Management Center version.

### Patches
CVE-2021-44228 is fixed in log4j 2.15.0.
CVE-2021-45046 is fixed in log4j 2.16.0.
CVE-2021-45105 is fixed in log4j 2.17.0.
CVE-2021-44832 is fixed in log4j 2.17.1.

As of 12/21/2021, Hazelcast team has released a new version of all affected products that upgrades log4j to 2.17.0 as listed below: 
Hazelcast Management Center 4.2021.12-1, Hazelcast Management Center 5.0.4.
Hazelcast IMDG and IMDG Enterprise 4.0.5, 4.1.8 and 4.2.4.
Hazelcast Jet 4.5.3.
Hazelcast Platform 5.0.2.

As of 01/06/2022, Hazelcast Management Center 4.2022.01 with the updated log4j 2.17.1 is released. log4j2.17.1 will be included in Management Center 5.1 that is expected to be released in February. 

Hazelcast recommends upgrading to the latest versions available.

### Workarounds
For users that an upgrade is not an option, below mitigations can be applied.

#### Disabling lookups via Environment Variable 
Setting the environment variable LOG4J_FORMAT_MSG_NO_LOOKUPS=true .
This option is the easiest to apply for containerized environments.

#### Disabling lookups in log4j2 configuration
Another good option since there is no need to replace JARs or no need to modify logging configuration file, users who cannot upgrade to 2.17.0 can mitigate the exposure by:

Users of Log4j 2.10 or greater may add `-Dlog4j2.formatMsgNoLookups=true `as a command line option or add `-Dlog4j2.formatMsgNoLookups=true` in a `log4j2.component.properties` file on the classpath to prevent lookups in log event messages.
Users since Log4j 2.7 may specify `%m{nolookups}` in the PatternLayout configuration to prevent lookups in log event messages.
As an example; users deploying Hazelcast Management Center via helm charts can do the following to disable lookups and restart in one command:

`helm upgrade <release-name> hazelcast/hazelcast --set mancenter.javaOpts="<javaOpts> -Dlog4j2.formatMsgNoLookups=true"`

Where <release-name> is the release name and <javaOpts> is existing java options user has added previously.

#### Removing the JndiLookup from classpath
Remove the JndiLookup and JndiManager classes from the log4j-core jar. Note that removal of the JndiManager will cause the JndiContextSelector and JMSAppender to no longer function.

### References
https://nvd.nist.gov/vuln/detail/CVE-2021-44228
https://nvd.nist.gov/vuln/detail/CVE-2021-45046
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-45105
https://nvd.nist.gov/vuln/detail/CVE-2021-44832
https://logging.apache.org/log4j/2.x/index.html

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [our repo](https://github.com/hazelcast/hazelcast)
* Slack us at [Hazelcast Community Slack](https://slack.hazelcast.com/)

## References
- https://github.com/hazelcast/hazelcast/security/advisories/GHSA-v57x-gxfj-484q
- https://github.com/hazelcast/hazelcast
