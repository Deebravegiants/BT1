# [M] FUXA has SQL Injection in its TDengine DAQ connector via backslash bypass of escapeTdString

## Summary
Severity: Medium
Advisory: GHSA-h9fj-c2qr-76g2
CVE: CVE-2026-47720
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-h9fj-c2qr-76g2
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0

## Details
## Summary

The TDengine DAQ storage connector's `escapeTdString` at `server/runtime/storage/tdengine/index.js:10` doubles single quotes but does not escape backslashes. TDengine's SQL parser treats `\'` as a literal single quote inside a string, so a tag id of the form `x\' OR 1=1--` escapes the first single quote, lets the doubled quote close the string, and appends an injected clause that runs on the TDengine server. An attacker (Alice) sends the crafted `sids` value through `GET /api/daq` or the Socket.IO `DAQ_QUERY` event and reads every row in `fuxa.meters`, which holds the historical tag values of every PLC the FUXA instance records.

## Details

The TDengine DAQ storage connector did not correctly sanitize user-controlled values before including them in SQL queries.

A specially crafted tag identifier could bypass the intended escaping logic and alter the query executed against the TDengine database.

This could allow unauthorized access to historical DAQ data stored in TDengine, including recorded tag values and related metadata.

The issue has been fixed in version 1.3.2 by improving input escaping in the TDengine connector.

## Impact

An attacker with network access to a FUXA instance configured with TDengine as the DAQ backend reads the entire historical tag-value archive: every PLC tag the instance has recorded, plus the associated device ids and device names. Turning on authentication does not close the gap: the Socket.IO `DAQ_QUERY` handler has no authorization check, and `/api/daq` accepts guest-level requests. No login is needed in the default configuration.

**CVSS 3.1**: `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` (Medium, 5.3). CWE-89.
---
A fix is available at https://github.com/frangoteam/FUXA/releases/tag/v1.3.2.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-h9fj-c2qr-76g2
- https://github.com/frangoteam/FUXA
