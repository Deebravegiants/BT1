# [H] Maven Archetype Plugin: Maven Archetype integration-test may package local settings into the published artifact, possibly containing credentials

## Summary
Severity: High
Advisory: CVE-2024-47197
Aliases: GHSA-2qq7-fch2-phqf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-47197
Type: osv

## Details
Exposure of Sensitive Information to an Unauthorized Actor, Insecure Storage of Sensitive Information vulnerability in Maven Archetype Plugin.

This issue affects Maven Archetype Plugin: from 3.2.1 before 3.3.0.

Users are recommended to upgrade to version 3.3.0, which fixes the issue.

Archetype integration testing creates a file
called ./target/classes/archetype-it/archetype-settings.xml
This file contains all the content from the users ~/.m2/settings.xml file,
which often contains information they do not want to publish. We expect that on many developer machines, this also contains
credentials.

When the user runs mvn verify again (without a mvn clean), this file becomes part of
the final artifact.

If a developer were to publish this into Maven Central or any other remote repository (whether as a release
or a snapshot) their credentials would be published without them knowing.

## References
- http://www.openwall.com/lists/oss-security/2024/09/26/2
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47197.json
- https://lists.apache.org/thread/ftg81np183wnyk0kg4ks95dvgxdrof96
- https://nvd.nist.gov/vuln/detail/CVE-2024-47197
