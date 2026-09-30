# [M] AutoGPT: SendEmailBlock's IP blocklist bypass allows SSRF via user-controlled SMTP server

## Summary
Severity: Medium
Advisory: CVE-2026-33234
Aliases: GHSA-4jwj-6mg5-wrwf
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-33234
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. In versions 0.1.0 through 0.6.51,  SendEmailBlock in autogpt_platform/backend/backend/blocks/email_block.py accepts a user-supplied smtp_server (string) and smtp_port (integer) as per-execution block inputs, then passes them directly to Python's smtplib.SMTP() to open a raw TCP connection with no IP address validation. This completely bypasses the platform's hardened SSRF protections in backend/util/request.py — the validate_url_host() function and BLOCKED_IP_NETWORKS blocklist that every other block uses to block connections to private, loopback, link-local, and cloud metadata addresses. An authenticated user on a shared AutoGPT deployment can use this to perform non-blind internal network port scanning and service fingerprinting: smtplib reads the target's TCP banner on connect and embeds it in the exception message, which is persisted as user-visible block output via the execution framework. This issue has been fixed in version 0.6.52.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33234.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-4jwj-6mg5-wrwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33234
