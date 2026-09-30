# [M] AVideo Unauthenticated Arbitrary File Write via aVideoEncoderChunk.json.php

## Summary
Severity: Medium
Advisory: CVE-2026-72748
Aliases: GHSA-v7p7-jccx-h37c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72748
Type: osv

## Details
AVideo contains an unauthenticated arbitrary file write vulnerability in the aVideoEncoderChunk.json.php endpoint that allows remote attackers to write up to 4 GB of arbitrary content to the server filesystem via HTTP PUT requests without authentication. Attackers can exhaust disk space causing denial of service, poison the video encoding pipeline, or chain this with local file inclusion to achieve remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72748.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-v7p7-jccx-h37c
- https://nvd.nist.gov/vuln/detail/CVE-2026-72748
- https://www.vulncheck.com/advisories/avideo-unauthenticated-arbitrary-file-write-via-avideoencoderchunk-json-php
- https://github.com/WWBN/AVideo/commit/1b55a9b3c4911d2f31594ce2e60566c70c6b95e8
