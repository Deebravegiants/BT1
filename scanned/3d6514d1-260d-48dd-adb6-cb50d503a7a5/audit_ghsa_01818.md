# [H] Execution Control List (ECL) Is Insecure in Singularity

## Summary
Severity: High
Advisory: GHSA-pmfr-63c2-jr5c
CVE: CVE-2020-13845
CWE: CWE-347, CWE-354
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-pmfr-63c2-jr5c
Type: github-advisory

## Affected
- Go: `github.com/sylabs/singularity` — affected >=3.0.0 <3.6.0

## Details
### Impact

The Singularity Execution Control List (ECL) allows system administrators to set up a policy that defines rules about what signature(s) must be (or must not be) present on a SIF container image for it to be permitted to run.

In Singularity 3.x versions below 3.6.0, the following issues allow the ECL to be bypassed by a malicious user:

 * Image integrity is not validated when an ECL policy is enforced.
 * The fingerprint required by the ECL is compared against the signature object descriptor(s) in the SIF file, rather than to a cryptographically validated signature. Thus, it is trivial to craft an arbitrary payload which will be permitted to run, even if the attacker does not have access to the private key associated with the fingerprint(s) configured in the ECL.

### Patches

These issues are addressed in Singularity 3.6.0.

All users are advised to upgrade to 3.6.0. Note that Singularity 3.6.0 uses a new signature format that is necessarily incompatible with Singularity < 3.6.0 - e.g. Singularity 3.5.3 cannot verify containers signed by 3.6.0.

Version 3.6.0 includes a `legacyinsecure` option that can be set to `legacyinsecure = true` in `ecl.toml` to allow the ECL to perform verification of the older, and insecure, legacy signatures for compatibility with existing containers. This does not guarantee that containers have not been modified since signing, due to other issues in the legacy signature format. The option should be used only to temporarily ease the transition to containers signed with the new 3.6.0 signature format.

### Workarounds

This issue affects any installation of Singularity configured to use the Execution Control List (ECL) functionality. There is no workaround if ECL is required.

### For more information

General questions about the impact of the advisory / changes made in the 3.6.0 release can be asked in the:

* [Singularity Slack Channel](https://bit.ly/2m0g3lX)
* [Singularity Mailing List](https://groups.google.com/a/lbl.gov/forum/??sdf%7Csort:date#!forum/singularity)

Any sensitive security concerns should be directed to: security@sylabs.io

See our Security Policy here: https://sylabs.io/security-policy

## References
- https://github.com/hpcng/singularity/security/advisories/GHSA-pmfr-63c2-jr5c
- https://nvd.nist.gov/vuln/detail/CVE-2020-13845
- https://medium.com/sylabs
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00053.html
