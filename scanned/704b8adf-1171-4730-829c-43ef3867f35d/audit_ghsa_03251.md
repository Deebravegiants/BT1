# [H] Incorrect handling of credential expiry by /nats-io/nats-server

## Summary
Severity: High
Advisory: GHSA-2c64-vj8g-vwrq
CWE: CWE-284
Ecosystem: Go
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-2c64-vj8g-vwrq
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.1.9

## Details
(This advisory is canonically https://advisories.nats.io/CVE/CVE-2020-26892.txt )

## Problem Description

NATS nats-server through 2020-10-07 has Incorrect Access Control because of how expired credentials are handled.

The NATS accounts system has expiration timestamps on credentials; the <https://github.com/nats-io/jwt> library had an API which encouraged misuse and an `IsRevoked()` method which misused its own API.

A new `IsClaimRevoked()` method has correct handling and the nats-server has been updated to use this.  The old `IsRevoked()` method now always returns true and other client code will have to be updated to avoid calling it.

The CVE identifier should cover any application using the old JWT API, where the nats-server is one of those applications.


## Affected versions

#### JWT library

 * all versions prior to 1.1.0
 * fixed after nats-io/jwt PR 103 landed (2020-10-06)

#### NATS Server

 * Version 2 prior to 2.1.9
   + 2.0.0 through and including 2.1.8 are vulnerable.
 * fixed with nats-io/nats-server PRs 1632, 1635, 1645


## Impact

Time-based credential expiry did not work.


## Workaround

Have credentials which only expire after fixes can be deployed.


## Solution

Upgrade the JWT dependency in any application using it.

Upgrade the NATS server if using NATS Accounts.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-2c64-vj8g-vwrq
- https://github.com/nats-io/jwt/commit/e11ce317263cef69619fc1ca743b195d02aa1d8a
- https://advisories.nats.io/CVE/CVE-2020-26892.txt
- https://github.com/nats-io/nats-server
