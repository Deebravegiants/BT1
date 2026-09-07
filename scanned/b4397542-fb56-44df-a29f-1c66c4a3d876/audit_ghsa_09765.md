# [C] Axios supply chain attack - dependency in @lightdash/cli may resolve to compromised axios versions

## Summary
Severity: Critical
Advisory: GHSA-3hfp-gqgh-xc5g
CWE: CWE-1395, CWE-508
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-3hfp-gqgh-xc5g
Type: github-advisory

## Affected
- npm: `@lightdash/cli` — affected >=0.1800.0 <0.2695.1

## Details
### Impact

A supply chain attack on the `axios` npm package (versions 1.14.1 and 0.30.4) introduced a malicious transitive dependency (`plain-crypto-js@4.2.1`) that deploys a cross-platform remote access trojan (RAT) on macOS, Windows, and Linux. The attacker compromised the primary axios maintainer's npm account to publish the malicious versions.

The malicious versions were live on npm for approximately 3 hours (00:21 UTC to 03:29 UTC on March 31, 2026) before being removed.

The `@lightdash/cli` package specified axios as a dependency with a semver range (`^1.12.0`) that permitted resolution to the compromised version. Any user who performed a fresh install of `@lightdash/cli` versions `>= 0.1800.0, < 0.2695.1` (without a pre-existing lockfile) during this window may have installed the malicious axios version.

If compromised, the RAT establishes a connection to a command-and-control server (`sfrclak[.]com` / `142.11.206.73:8000`) and provides the attacker with shell access, file system enumeration, and the ability to execute arbitrary commands. All credentials, secrets, and tokens accessible from the affected machine should be considered compromised.

Lightdash Cloud is not affected.

### Patches

This has been patched in `@lightdash/cli@0.2695.1`. The fix pins axios to a known safe version (1.14.0).

Users should upgrade immediately:

```
npm install -g @lightdash/cli@0.2695.1
```

If users had installed the compromised version, they should check for RAT artifacts before and after upgrading:

- macOS: `/Library/Caches/com.apple.act.mond`
- Windows: `%PROGRAMDATA%\wt.exe`
- Linux: `/tmp/ld.py`

If any artifacts are found, assume full compromise of that machine and rotate all accessible credentials (warehouse credentials, API tokens, SSH keys, cloud provider credentials, environment variables).

### Workarounds

If users cannot upgrade immediately, they can force a safe axios resolution after installing the CLI:

```
npm install -g axios@1.14.0 --force
```

Alternatively, if users are building a Docker image or using a lockfile, they should ensure their resolved axios version is not 1.14.1 or 0.30.4:

```
npm ls axios
```

Block egress traffic to `sfrclak[.]com` and `142.11.206.73` at the network level to prevent the RAT from reaching its command-and-control server.

### Resources

- Upstream axios issue: https://github.com/axios/axios/issues/10604
- StepSecurity analysis: https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan
- Socket analysis: https://socket.dev/blog/axios-npm-package-compromised
- Snyk advisory (axios): https://security.snyk.io/vuln/SNYK-JS-AXIOS-15850650
- Snyk advisory (plain-crypto-js): https://security.snyk.io/vuln/SNYK-JS-PLAINCRYPTOJS-15850652
- The Hacker News coverage: https://thehackernews.com/2026/03/axios-supply-chain-attack-pushes-cross.html

## References
- https://github.com/lightdash/lightdash/security/advisories/GHSA-3hfp-gqgh-xc5g
- https://github.com/axios/axios/issues/10604
- https://github.com/advisories/GHSA-fw8c-xr5c-95f9
- https://github.com/lightdash/lightdash
- https://security.snyk.io/vuln/SNYK-JS-AXIOS-15850650
- https://security.snyk.io/vuln/SNYK-JS-PLAINCRYPTOJS-15850652
- https://socket.dev/blog/axios-npm-package-compromised
- https://thehackernews.com/2026/03/axios-supply-chain-attack-pushes-cross.html
- https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan
