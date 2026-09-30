# [M] sigstore-js has Insufficient Verification of Data Authenticity

## Summary
Severity: Medium
Advisory: GHSA-xgjw-pm74-86q4
CVE: CVE-2026-48816
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-xgjw-pm74-86q4
Type: github-advisory

## Affected
- npm: `@sigstore/verify` — affected >=3.1.0 <3.1.1

## Details
sigstore-js derives a transparency-log timestamp from `tlogEntries[].integratedTime` and uses it to validate certificate validity windows and satisfy `timestampThreshold`. For bundle v0.2, a tlog entry can be inclusionProof-only (no signed inclusionPromise/set), and the inclusion proof path does not cryptographically bind `integratedTime`. As a result, an attacker who can supply an untrusted bundle can influence time-based verification decisions by choosing `integratedTime`.

## impact
If a consumer accepts attacker-provided bundle v0.2 inputs and relies on tlog-derived timestamps for certificate validity checks, verification can be influenced by an unauthenticated timestamp value. This is a trust gap: `integratedTime` is treated as a trusted observer timestamp under inclusionProof-only mode even though only the signed inclusionPromise/set path binds it.

## affected code
- `packages/verify/src/bundle/index.ts` (adds a transparency-log timestamp whenever `integratedTime != 0`)
- `packages/verify/src/timestamp/index.ts` (converts `integratedTime` to a `Date`)
- `packages/verify/src/verifier.ts` (verifies timestamps before verifying tlog inclusion)
- `packages/verify/src/tlog/index.ts` + `packages/verify/src/tlog/set.ts` (only the inclusionPromise/set path binds `integratedTime`)

## proof of concept
The attached `poc.zip` contains a self-contained harness that reproduces the behavior on the pinned commit and includes both a canonical test and a negative control.

repro:
1) extract `poc.zip` into a fresh directory and run the make targets:

```bash
unzip poc.zip -d poc
cd poc/poc-F-SIG-JS-TLOGTIME-001
make canonical
make control
```

2) confirm `canonical.log` includes:

```
[CALLSITE_HIT]:
[PROOF_MARKER]:
```

3) confirm `control.log` includes:

```
[NC_MARKER]:
```

## suggested fix
Only treat `integratedTime` as a trusted timestamp when it is cryptographically bound (for example, via a verified signed inclusionPromise/set). For inclusionProof-only entries, do not count `integratedTime` toward `timestampThreshold`, and do not use it for certificate validity decisions unless there is another signed time source (for example, an rfc3161 timestamp).

[poc.zip](https://github.com/user-attachments/files/25643656/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25643660/PR_DESCRIPTION.md)
[SUBMISSION.md](https://github.com/user-attachments/files/25643662/SUBMISSION.md)

## References
- https://github.com/sigstore/sigstore-js/security/advisories/GHSA-xgjw-pm74-86q4
- https://github.com/sigstore/sigstore-js
