# [H] MISP CurlClient TLS Peer Verification Disabled by Default Enables Man-in-the-Middle Attacks

## Summary
Severity: High
Advisory: CVE-2026-85221
CVSS: 7.5 (CVSS:4.0/AV:A/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85221
Type: osv

## Details
MISP contains an improper TLS certificate validation vulnerability in CurlClient. The CurlClient::$verifyPeer property was not explicitly initialized and therefore defaulted to null. When passed to cURL, this value effectively disabled TLS peer verification unless the calling code explicitly enabled it.


As a result, HTTPS connections made through affected CurlClient instances could accept certificates that were not issued by a trusted certificate authority. An attacker capable of intercepting or manipulating network traffic between a MISP instance and a remote HTTPS service could impersonate the remote endpoint and perform a man-in-the-middle attack.


Successful exploitation could allow an attacker to observe sensitive information transmitted by MISP, including authentication material or exchanged threat intelligence, and to modify responses returned to the MISP instance. The impact depends on the functionality using CurlClient and the data exchanged with the remote service.


The patch enables TLS peer verification by default while preserving explicit support for configured self-signed certificates. It also corrects the self-signed certificate handling in SyncTool so that peer verification is disabled only when no pinned CA certificate is configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85221.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85221
- https://github.com/MISP/MISP/commit/e06f69858
- https://github.com/MISP/MISP
