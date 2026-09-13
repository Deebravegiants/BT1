# [H] Information disclosure in SSB-DB

## Summary
Severity: High
Advisory: GHSA-mpgr-2cx9-327h
CVE: CVE-2020-4045
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-11
Source: https://github.com/advisories/GHSA-mpgr-2cx9-327h
Type: github-advisory

## Affected
- npm: `ssb-db` — affected >=20.0.0 <20.0.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Servers running SSB-DB 20.0.0 (which is packaged with SSB-Server 16.0.0) must upgrade immediately.

**There is no evidence that other SSB apps are vulnerable or that this problem has been exploited in the wild.**

The `get()` method is supposed to only decrypt messages when you explicitly ask it to, but there's a bug where it's decrypting any message that it can. This means that it's returning the decrypted content of private messages, which a malicious peer could use to get access to private data. This only affects peers running SSB-DB@20.0.0 who also have private messages, and is only known to be exploitable if you're also running SSB-OOO (default in SSB-Server), which exposes a thin wrapper around `get()` to anonymous peers.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Yes, please upgrade to SSB-DB 20.0.1 (or SSB-Server 16.0.1) immediately.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

You may be able to disable the most obvious attack vector, SSB-OOO, by disabling the plugin, but you should upgrade immediately anyway.

### For more information

If you have any questions or comments about this advisory, open an issue in [SSB-DB](https://github.com/ssbc/ssb-db/)

## References
- https://github.com/ssbc/ssb-db/security/advisories/GHSA-mpgr-2cx9-327h
- https://nvd.nist.gov/vuln/detail/CVE-2020-4045
- https://github.com/ssbc/ssb-db/commit/43334d0871c9cc6220e0f6d6338499060f7761d4
