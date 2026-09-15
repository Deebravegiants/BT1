# [M] CVE-2021-21253

## Summary
Severity: Medium
Advisory: CVE-2021-21253
Aliases: GHSA-wwg8-372v-v332
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-01-21
Source: https://osv.dev/vulnerability/CVE-2021-21253
Type: osv

## Details
OnlineVotingSystem is an open source project hosted on GitHub. OnlineVotingSystem before version 1.1.2 hashes user passwords without a salt, which is vulnerable to dictionary attacks. Therefore there is a threat of security breach in the voting system. Without a salt, it is much easier for attackers to pre-compute the hash value using dictionary attack techniques such as rainbow tables to crack passwords. This problem is fixed and published in version 1.1.2. A long randomly generated salt is added to the password hash function to better protect passwords stored in the voting system.

## References
- https://github.com/dbijaya/OnlineVotingSystem/security/advisories/GHSA-wwg8-372v-v332
- https://github.com/dbijaya/OnlineVotingSystem/commit/0181cb0272857696c8eb3e44fcf6cb014ff90f09
