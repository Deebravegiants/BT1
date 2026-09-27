# [C] External Control of System or Configuration Setting and Uncontrolled Search Path Element in sfw

## Summary
Severity: Critical
Advisory: CVE-2025-64726
Aliases: GHSA-6c5p-vqrh-h6fp
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64726
Type: osv

## Details
Socket Firewall is an HTTP/HTTPS proxy server that intercepts package manager requests and enforces security policies by blocking dangerous packages. Socket Firewall binary versions (separate from installers) prior to 0.15.5 are vulnerable to arbitrary code execution when run in untrusted project directories. The vulnerability allows an attacker to execute arbitrary code by placing a malicious `.sfw.config` file in a project directory. When a developer runs Socket Firewall commands (e.g., `sfw npm install`) in that directory, the tool loads the `.sfw.config` file and populates environment variables directly into the Node.js process. An attacker can exploit this by setting `NODE_OPTIONS` with a `--require` directive to execute malicious JavaScript code before Socket Firewall's security controls are initialized, effectively bypassing the tool's malicious package detection. The attack vector is indirect and requires a developer to install dependencies for an untrusted project and execute a command within the context of the untrusted project. The vulnerability has been patched in Socket Firewall version 0.15.5. Users should upgrade to version 0.15.5 or later. The fix isolates configuration file values from subprocess environments. Look at `sfw --version` for version information. If users rely on the recommended installation mechanism (e.g. global installation via `npm install -g sfw`) then no workaround is necessary. This wrapper package automatically ensures that users are running the latest version of Socket Firewall. Users who have manually installed the binary and cannot immediately upgrade should avoid running Socket Firewall in untrusted project directories. Before running Socket Firewall in any new project, inspect `.sfw.config` and `.env.local` files for suspicious `NODE_OPTIONS` or other environment variable definitions that reference local files.

## References
- https://bsky.app/profile/evilpacket.net/post/3m4iylwxtns2t
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64726.json
- https://github.com/SocketDev/firewall-release/security/advisories/GHSA-6c5p-vqrh-h6fp
- https://nvd.nist.gov/vuln/detail/CVE-2025-64726
