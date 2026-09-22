# [H] OpenAM Unauthenticated Session Hijacking via Information Exposure in CDCServlet

## Summary
Severity: High
Advisory: GHSA-r9pv-5rpp-vm8g
CVE: CVE-2026-45049
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-r9pv-5rpp-vm8g
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-federation` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Information Exposure Through Sent Data (CWE-201) issue in OpenAM's Cross-Domain Single Sign-On (CDSSO) servlet allows a logged-in user's raw OpenAM session token to be POSTed to an attacker-controlled URL. This impacts OpenAM Community Edition through version 16.0.6. This issue was patched in version 16.1.1.

An attacker who can induce a logged-in victim to visit a crafted URL may receive the victim's session credential, which could enable session hijacking.

## Impact
OpenAM deployments through version 16.0.6 that have CDSSO enabled are potentially affected. The CDSSO component is commonly enabled in multi-domain deployments. Exploitation requires user interaction — an authenticated user must be induced to visit an attacker-crafted URL — and is further gated on a non-default configuration being absent.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-r9pv-5rpp-vm8g
- https://github.com/OpenIdentityPlatform/OpenAM
