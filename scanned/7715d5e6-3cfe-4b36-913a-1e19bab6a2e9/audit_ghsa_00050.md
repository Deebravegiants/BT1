# [H] Remote Code Execution in electron

## Summary
Severity: High
Advisory: GHSA-w222-53c6-c86p
CVE: CVE-2018-1000006
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-01-23
Source: https://github.com/advisories/GHSA-w222-53c6-c86p
Type: github-advisory

## Affected
- npm: `electron` — affected >=1.7.0 <1.7.11
- npm: `electron` — affected >=1.6.0 <1.6.16
- npm: `electron` — affected >=1.8.0 <1.8.2-beta.4

## Details
Affected versions of `electron` may be susceptible to a remote code execution flaw when certain conditions are met:
1. The electron application is running on Windows.
2. The electron application registers as the default handler for a protocol, such as `nodeapp://`.

This vulnerability is caused by a failure to sanitize additional arguments to chromium in the command line handler for Electron.

MacOS and Linux are not vulnerable.


## Recommendation

Update electron to a version that is not vulnerable. If updating is not possible, the electron team has provided the following guidance:


If for some reason you are unable to upgrade your Electron version, you can append `--` as the last argument when calling `app.setAsDefaultProtocolClient`, which prevents Chromium from parsing further options. The double dash `--` signifies the end of command options, after which only positional parameters are accepted.
```
app.setAsDefaultProtocolClient(protocol, process.execPath, [
  '--your-switches-here',
  '--'
])
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000006
- https://electronjs.org/blog/protocol-handler-fix
- https://github.com/advisories/GHSA-w222-53c6-c86p
- https://github.com/electron/electron/releases/tag/v1.8.2-beta.4
- https://medium.com/@Wflki/exploiting-electron-rce-in-exodus-wallet-d9e6db13c374
- https://www.exploit-db.com/exploits/43899
- https://www.exploit-db.com/exploits/44357
- https://www.npmjs.com/advisories/563
- http://www.securityfocus.com/bid/102796
