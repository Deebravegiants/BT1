# [C] BeWelcome/Rox PHP Object Injection RCE

## Summary
Severity: Critical
Advisory: CVE-2025-34292
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-34292
Type: osv

## Details
Rox, the software running BeWelcome, contains a PHP object injection vulnerability resulting from deserialization of untrusted data. User-controlled input is passed to PHP's unserialize(): the POST parameter `formkit_memory_recovery` in \\RoxPostHandler::getCallbackAction and the 'memory cookie' read by \\RoxModelBase::getMemoryCookie (bwRemember). (1) If present, `formkit_memory_recovery` is processed and passed to unserialize(), and (2) restore-from-memory functionality calls unserialize() on the bwRemember cookie value. Gadget chains present in Rox and bundled libraries enable exploitation of object injection to write arbitrary files or achieve remote code execution. Successful exploitation can lead to full site compromise. This vulnerability was remediated with commit c60bf04 (2025-06-16).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34292.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34292
- https://www.vulncheck.com/advisories/rox-php-object-injection-rce
- https://github.com/BeWelcome/rox/commit/c60bf04
- https://github.com/BeWelcome/rox
- https://gist.github.com/mcdruid/c0f7c42b28949c7d86cf77d0c674f398
