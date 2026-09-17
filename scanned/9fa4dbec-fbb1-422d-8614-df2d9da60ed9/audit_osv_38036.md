# [C] AVideo has SQL Injection in Live_schedule::keyExists() via Unparameterized Stream Key

## Summary
Severity: Critical
Advisory: CVE-2026-34374
Aliases: GHSA-xgv5-66wp-ch88
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-34374
Type: osv

## Details
WWBN AVideo is an open source video platform. In versions up to and including 26.0, the `Live_schedule::keyExists()` method constructs a SQL query by interpolating a stream key directly into the query string without parameterization. This method is called as a fallback from `LiveTransmition::keyExists()` when the initial parameterized lookup returns no results. Although the calling function correctly uses parameterized queries for its own lookup, the fallback path to `Live_schedule::keyExists()` undoes this protection entirely. This vulnerability is distinct from GHSA-pvw4-p2jm-chjm, which covers SQL injection via the `live_schedule_id` parameter in the reminder function. This finding targets the stream key lookup path used during RTMP publish authentication. As of time of publication, no patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34374.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xgv5-66wp-ch88
- https://nvd.nist.gov/vuln/detail/CVE-2026-34374
