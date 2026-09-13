# [M] Netflix/Priam: Temporary Directory Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-f4jh-ww96-9h9j
CVE: CVE-2021-28100
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-30
Source: https://github.com/advisories/GHSA-f4jh-ww96-9h9j
Type: github-advisory

## Affected
- Maven: `com.netflix.priam:priam` — affected >=0

## Details
### Impact

When `File.createTempFile` creates a file, the permissions on that file are -rw-r--r--. This means that other users can read the contents of these files after they are written, although they can not modify the contents. This allows for local information disclosure if these files contain sensitive information.

Vulnerable locations:
 - https://github.com/Netflix/Priam/blob/362660bb7ebddb0cfa756a282d94678f65af9f06/priam/src/main/java/com/netflix/priam/backup/MetaData.java#L106-L111
 - https://github.com/Netflix/Priam/blob/362660bb7ebddb0cfa756a282d94678f65af9f06/priam/src/main/java/com/netflix/priam/identity/DoubleRing.java#L109-L118
 - https://github.com/Netflix/Priam/blob/362660bb7ebddb0cfa756a282d94678f65af9f06/priam/src/main/java/com/netflix/priam/restore/PostRestoreHook.java#L80-L86

---

The custom CodeQL queries leveraged to find these this as well as their results can be found here:

https://lgtm.com/query/1543383251073929777/
https://lgtm.com/query/3142895023158674709/

## Official Disclosure

https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2021-002.md

## Fix

There are no fixed versions.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-f4jh-ww96-9h9j
