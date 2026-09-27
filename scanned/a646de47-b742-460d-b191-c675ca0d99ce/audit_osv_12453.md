# [H] CVE-2018-12120

## Summary
Severity: High
Advisory: CVE-2018-12120
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-12120
Type: osv

## Details
Node.js: All versions prior to Node.js 6.15.0: Debugger port 5858 listens on any interface by default: When the debugger is enabled with `node --debug` or `node debug`, it listens to port 5858 on all interfaces by default. This may allow remote computers to attach to the debug port and evaluate arbitrary JavaScript. The default interface is now localhost. It has always been possible to start the debugger on a specific interface, such as `node --debug=localhost`. The debugger was removed in Node.js 8 and replaced with the inspector, so no versions from 8 and later are vulnerable.

## References
- http://www.securityfocus.com/bid/106040
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
