# [H] Nil dereference in NATS JWT causing DoS of nats-server

## Summary
Severity: High
Advisory: GHSA-hmm9-r2m2-qg9w
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-hmm9-r2m2-qg9w
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.1.9

## Details
(This advisory is canonically <https://advisories.nats.io/CVE/CVE-2020-26521.txt>)

## Problem Description

The NATS account system has an Operator trusted by the servers, which signs Accounts, and each Account can then create and sign Users within their account.  The Operator should be able to safely issue Accounts to other entities which it does not fully trust.

A malicious Account could create and sign a User JWT with a state not created by the normal tooling, such that decoding by the NATS JWT library (written in Go) would attempt a nil dereference, aborting execution.

The NATS Server is known to be impacted by this.


## Affected versions

#### JWT library

 * all versions prior to 1.1.0

#### NATS Server

 * Version 2 prior to 2.1.9


## Impact

#### JWT library

 * Programs would nil dereference and panic, aborting execution by default.

#### NATS server

 * Denial of Service caused by process termination


## Workaround

If your NATS servers do not trust any accounts which are managed by untrusted entities, then malformed User credentials are unlikely to be encountered.


## Solution

Upgrade the JWT dependency in any application using it.

Upgrade the NATS server if using NATS Accounts.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-hmm9-r2m2-qg9w
- https://nvd.nist.gov/vuln/detail/CVE-2020-26521
- https://github.com/nats-io/jwt/pull/107
- https://advisories.nats.io/CVE/CVE-2020-26521.txt
- https://github.com/nats-io/nats-server
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VT67XCLIIBYRT762SVFBYFFTQFVSM3SI
- https://www.openwall.com/lists/oss-security/2020/11/02/2
