# [M] Nuclei: Local File Read via require() Module Loader Bypass

## Summary
Severity: Medium
Advisory: GHSA-29rg-wmcw-hpf4
CVE: CVE-2026-41646
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-29rg-wmcw-hpf4
Type: github-advisory

## Affected
- Go: `github.com/projectdiscovery/nuclei/v3` — affected >=3.0.0 <3.8.0

## Details
A vulnerability in Nuclei's JavaScript protocol runtime allows JavaScript templates to read local `.js` and `.json` files through the `require()` function, bypassing the default local file access restriction.

**Affected Component**

The issue is in the JavaScript runtime's module loading system. The goja `require()` function used a default host filesystem loader without routing through the `allow-local-file-access` check.

**Description**

The goja require() function in Nuclei's JavaScript protocol runtime used the default host filesystem loader, which allowed JavaScript templates to import .js and .json files from anywhere on the host filesystem, ignoring the allow-local-file-access (-lfa) option that controls file access outside the template directory.

The impact is limited to `.js` and `.json` files, as goja's module loader only resolves those extensions. That said, this is still enough to expose sensitive data stored in JSON configuration files like `package.json`, credential stores, or cloud configuration files sitting on the host filesystem.

**Affected Users**

- **CLI users** running untrusted or third-party JavaScript templates.
- **SDK users** who have integrated Nuclei into platforms where end-users can supply JavaScript templates, especially when relying on the default file access restriction to limit filesystem reads.

> [!NOTE]
The `require()` module loader only resolves `.js` and `.json` files. Other file types cannot be read through this vector.

**Patches**

- The vulnerability is fixed in Nuclei v3.8.0. Upgrading is strongly recommended. 
- Fix reference: #7332

**Mitigation**

Upgrade to Nuclei v3.8.0, where the `require()` registry is rebuilt per execution and file-backed module loads are routed through the same `allow-local-file-access` check as the rest of the filesystem operations.

In the meantime, avoid running JavaScript templates from unverified sources.

**Workarounds**

If upgrading is not an option, avoid running untrusted JavaScript templates entirely. There is no flag or configuration that mitigates this on affected versions.

**Acknowledgments**

Nuceli thanks @AkashHamal0x01 for reporting this issue through responsible disclosure via security@projectdiscovery.io

## References
- https://github.com/projectdiscovery/nuclei/security/advisories/GHSA-29rg-wmcw-hpf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41646
- https://github.com/projectdiscovery/nuclei/pull/7332
- https://github.com/projectdiscovery/nuclei/commit/6f2ade6a9b427c284c15a43445f9c7f055e60e5d
- https://github.com/projectdiscovery/nuclei
