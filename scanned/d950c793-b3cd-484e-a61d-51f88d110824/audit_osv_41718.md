# [H] Deskflow: Odd-length DSOP options vector causes out-of-bounds read in Deskflow client

## Summary
Severity: High
Advisory: CVE-2026-63409
Aliases: GHSA-gmvh-3c73-m5gg
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-63409
Type: osv

## Details
Deskflow is a keyboard and mouse sharing app. From 1.17.0 until continuous build 1.26.0.296, a malicious Deskflow server can send an odd-length DSOP vector to ServerProxy::setOptions() in src/lib/client/ServerProxy.cpp, causing the missing value after the final option key to be read beyond the vector during the PacketStreamFilter::filterEvent to ServerProxy::handleData() to ServerProxy::parseHandshakeMessage() call chain and crash the connected client. This issue is fixed in continuous build 1.26.0.296.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63409.json
- https://github.com/deskflow/deskflow/security/advisories/GHSA-gmvh-3c73-m5gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-63409
- https://github.com/deskflow/deskflow/commit/8266fbbe6af93fa370018886c7f1f35d2cee8b3f
