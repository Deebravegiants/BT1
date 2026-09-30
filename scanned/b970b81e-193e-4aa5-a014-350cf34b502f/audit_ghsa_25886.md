# [H] Arbitrary file write in nats-server

## Summary
Severity: High
Advisory: GHSA-6h3m-36w8-hv68
CVE: CVE-2022-26652
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-6h3m-36w8-hv68
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.2.0 <2.7.4
- Go: `github.com/nats-io/nats-streaming-server` — affected >=0.15.0 <0.24.3

## Details
(This document is canonically: <https://advisories.nats.io/CVE/CVE-2022-26652.txt>)

## Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

JetStream is the optional RAFT-based resilient persistent feature of NATS.


## Problem Description

The JetStream streams can be backed up and restored via NATS. The backup format is a tar archive file.  Inadequate checks on the filenames within the archive file permit a so-called "Zip Slip" attack in the stream restore.

NATS nats-server through 2022-03-09 (fixed in release 2.7.4) did not correctly sanitize elements of the archive file, thus a user of NATS
could cause the NATS server to write arbitrary content to an attacker-controlled filename.


## Affected versions

NATS Server:
 * 2.2.0 up to and including 2.7.3.
   + Introduced with JetStream Restore functionality
 * Fixed with nats-io/nats-server: 2.7.4
 * Docker image:  nats <https://hub.docker.com/_/nats>
 * NB users of OS package files from our releases: a change in goreleaser defaults, discovered late in the release process, moved the install directory from /usr/local/bin to /usr/bin; we are evaluating the correct solution for subsequent releases, but not recutting this release.

NATS Streaming Server
 * 0.15.0 up to and including 0.24.2
 * Fixed with nats-io/nats-streaming-server: 0.24.3
 * Embeds a nats-server, but this server is the old approach which JetStream replaces, so unlikely (but not impossible) to be
   configured with JS support


## Workarounds

 * Disable JetStream for untrusted users.
 * If only one NATS account uses JetStream, such that cross-user attacks are not an issue, and any user in that account with access to the JetStream API is fully trusted anyway, then appropriate sandboxing techniques will prevent exploit.
   + Eg, with systemd, the supplied util/nats-server-hardened.service example configuration demonstrates that NATS runs fine as an unprivileged user under ProtectSystem=strict and PrivateTmp=true restrictions; by only opening a ReadWritePaths hole for the JetStream storage area, the impact of this vulnerability is limited.


## Solution

Upgrade the NATS server to at least 2.7.4.

We fully support the util/nats-server-hardened.service configuration for running a NATS server and encourage this approach.


## Credits

This issue was reported (on 2022-03-07) to the NATS Maintainers by
Yiming Xiang, TIANJI LAB of NSFOCUS.  
Thank you / 谢谢你！

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-6h3m-36w8-hv68
- https://nvd.nist.gov/vuln/detail/CVE-2022-26652
- https://github.com/nats-io/nats-server/pull/2917
- https://advisories.nats.io/CVE/CVE-2022-26652.txt
- https://github.com/nats-io/nats-server
- https://github.com/nats-io/nats-server/releases
- https://github.com/nats-io/nats-server/releases/tag/v2.7.4
- https://github.com/nats-io/nats-streaming-server/releases/tag/v0.24.3
- http://www.openwall.com/lists/oss-security/2022/03/10/1
