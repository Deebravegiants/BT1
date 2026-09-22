# [H] Uncontrolled Recursion and Asymmetric Resource Consumption (Amplification) in media/file proxy in Misskey

## Summary
Severity: High
Advisory: CVE-2024-49363
Aliases: GHSA-gq5q-c77c-v236
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:H)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-49363
Type: osv

## Details
Misskey is an open source, federated social media platform. In affected versions FileServerService (media proxy) in github.com/misskey-dev/misskey 2024.10.1 or earlier did not detect proxy loops, which allows remote actors to execute a self-propagating reflected/amplified distributed denial-of-service via a maliciously crafted note. FileServerService.prototype.proxyHandler did not check incoming requests are not coming from another proxy server. An attacker can execute an amplified denial-of-service by sending a nested proxy request to the server and end the request with a malicious redirect back to another nested proxy request.
Leading to unbounded recursion until the original request is timed out. This issue has been addressed in version 2024.11.0-alpha.3. Users are advised to upgrade. Users unable to upgrade may configure the reverse proxy to block requests to the proxy with an empty User-Agent header or one containing Misskey/. An attacker can not effectively modify the User-Agent header without making another request to the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49363.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-gq5q-c77c-v236
- https://nvd.nist.gov/vuln/detail/CVE-2024-49363
