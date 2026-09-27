# [M] Insecure temporary file in Netflix OSS Hollow

## Summary
Severity: Medium
Advisory: GHSA-9295-mhf3-v33m
CVE: CVE-2021-28099
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-9295-mhf3-v33m
Type: github-advisory

## Affected
- Maven: `com.netflix.hollow:hollow` — affected >=0

## Details
> ID: NFLX-2021-001
> Title: Local information disclosure in Hollow
> Release Date: 2021-03-23
> Credit: Security Researcher @JLLeitschuh

# Overview

Security researcher @JLLeitschuh reported that Netflix Hollow (a Netflix OSS project available here: https://github.com/Netflix/hollow) writes to a local temporary directory before validating the permissions on it.

# Impact

An attacker with the ability to create directories and set permissions on the local filesystem could pre-create this directory and read or modify anything written there by the Hollow process.

# Description

Since the `Files.exists(parent)` is run before creating the directories, an attacker can pre-create these directories with wide permissions. Additionally, since an insecure source of randomness is used, the file names to be created can be deterministically calculated.

# Workarounds and Fixes

Avoid running Hollow in configurations that share a filesystem with less-trusted processes. May be fixed in a future release.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-j83w-7qr9-wv86
- https://nvd.nist.gov/vuln/detail/CVE-2021-28099
- https://github.com/Netflix/hollow/issues/502
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2021-001.md
