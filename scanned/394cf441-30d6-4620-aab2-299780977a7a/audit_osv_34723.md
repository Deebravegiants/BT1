# [H] Suricata is vulnerable to a stack overflow from unbounded stack allocation in LuaPushStringBuffer

## Summary
Severity: High
Advisory: CVE-2025-64344
Aliases: GHSA-93fh-cgmc-w3rx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64344
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Prior to versions 7.0.13 and 8.0.2, working with large buffers in Lua scripts can lead to a stack overflow. Users of Lua rules and output scripts may be affected when working with large buffers. This includes a rule passing a large buffer to a Lua script. This issue has been patched in versions 7.0.13 and 8.0.2. A workaround for this issue involves disabling Lua rules and output scripts, or making sure limits, such as stream.depth.reassembly and HTTP response body limits (response-body-limit), are set to less than half the stack size.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64344.json
- https://github.com/OISF/suricata/security/advisories/GHSA-93fh-cgmc-w3rx
- https://nvd.nist.gov/vuln/detail/CVE-2025-64344
- https://github.com/OISF/suricata/commit/e13fe6a90dba210a478148c4084f6f5db17c5b5a
