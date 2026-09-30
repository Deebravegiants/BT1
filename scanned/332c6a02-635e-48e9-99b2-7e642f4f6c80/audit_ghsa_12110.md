# [H] Magic Wormhole: "wormhole receive" allows arbitrary local file overwrite

## Summary
Severity: High
Advisory: GHSA-4g4c-mfqg-pj8r
CVE: CVE-2026-32116
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4g4c-mfqg-pj8r
Type: github-advisory

## Affected
- PyPI: `magic-wormhole` — affected >=0.21.0 <0.23.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Receiving a file (`wormhole receive`) from a malicious party could result in overwriting critical local files, including `~/.ssh/authorized_keys` and `.bashrc`. This could be used to compromise the receiver's computer.

Only the sender of the file (the party who runs `wormhole send`) can mount the attack. Other parties (including the transit/relay servers) are excluded by the wormhole protocol.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

The bug has been fixed in magic-wormhole 0.23.0. All users should upgrade to this version.

The vulnerability first surfaced in the 0.21.0 release on 23-Oct-2025.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

As a workaround, the receiver can override the sender's filename with the `--output` or `-o` option. For example: `wormhole receive -o shopping-list.txt` will write the file to `shopping-list.txt` in the local directory, regardless of what the sender tries to do. To be effective, this option must be added to every invocation of `wormhole receive` / `wormhole rx`.

### References
_Are there any links users can visit to find out more?_

Incoming file transfer requests include a `filename`, used to decide where the file contents will be written. Well-behaving senders compute this from the `basename()` of the sent file (which discards all but the last segment of the path). To guard against malicious senders, the receiver also applies `basename()` to the incoming filename. During refactoring in version 0.21.0, this receiver-side check was accidentally dropped. The check was restored in version 0.23.0 along with a unit test.

Many thanks to Ian McKenzie (@ikmckenz) for spotting the bug and reaching out with a fix.

## References
- https://github.com/magic-wormhole/magic-wormhole/security/advisories/GHSA-4g4c-mfqg-pj8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32116
- https://github.com/magic-wormhole/magic-wormhole
