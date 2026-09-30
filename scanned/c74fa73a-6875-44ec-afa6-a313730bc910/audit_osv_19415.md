# [H] CVE-2021-21251

## Summary
Severity: High
Advisory: CVE-2021-21251
Aliases: GHSA-2w6j-wc8c-9mq2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21251
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3 there is a critical "zip slip" vulnerability. This issue may lead to arbitrary file write. The KubernetesResource REST endpoint untars user controlled data from the request body using TarUtils. TarUtils is a custom library method leveraging Apache Commons Compress. During the untar process, there are no checks in place to prevent an untarred file from traversing the file system and overriding an existing file. For a successful exploitation, the attacker requires a valid __JobToken__ which may not be possible to get without using any of the other reported vulnerabilities. But this should be considered a vulnerability in `io.onedev.commons.utils.TarUtils` since it lives in a different artifact and can affect other projects using it. This issue was addressed in 4.0.3 by validating paths in tar archive to only allow them to be in specified folder when extracted.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-2w6j-wc8c-9mq2
