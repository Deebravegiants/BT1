# [M] pnpm Has an Integrity Check Bypass via Missing Lockfile Integrity Field

## Summary
Severity: Medium
Advisory: GHSA-q6j5-fjx5-2mc3
CVE: CVE-2026-50021
CWE: CWE-354
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-q6j5-fjx5-2mc3
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=11.0.0 <11.4.0
- npm: `pnpm` — affected >=0 <10.34.1

## Details
## Summary

pnpm's tarball extraction worker skips integrity verification when the `integrity` field is absent from the lockfile resolution. If an attacker can both modify `pnpm-lock.yaml` to remove the `integrity:` field and cause the referenced registry URL to serve altered package content, `pnpm install --frozen-lockfile` can install the altered package without an integrity error. npm's `npm ci` enforces integrity by default; pnpm's behavior of silently skipping verification is a pnpm-specific fail-open gap.

## Vulnerability Details

The `addTarballToStore` function in `worker/src/start.ts` (lines 189-204) checks `if (integrity)` before verifying the tarball hash. The `TarballResolution` type declares `integrity` as optional (`integrity?: string`). When the lockfile omits the `integrity` field, the guard evaluates to `false`, skipping hash verification entirely. The worker then computes a new hash from the unverified content and stores it as legitimate.

```typescript
// worker/src/start.ts:189-204
function addTarballToStore ({ buffer, storeDir, integrity, ... }: TarballExtractMessage) {
  if (integrity) {           // false when integrity is undefined
    const { algorithm, hexDigest } = parseIntegrity(integrity)
    const calculatedHash = crypto.hash(algorithm, buffer, 'hex')
    if (calculatedHash !== hexDigest) {
      return { status: 'error', error: { type: 'integrity_validation_failed', ... } }
    }
  }
  return {
    status: 'success',
    value: { integrity: integrity ?? calcIntegrity(buffer) },
  }
}
```

## Proof of Concept

```bash
bash autofyn_audit/exploits/vuln1_integrity_bypass/exploit.sh
# Publishes a package, generates lockfile, republishes tampered version,
# strips integrity field, re-runs install --frozen-lockfile.
# Result: PASS -- tampered package installed without integrity error.
```

## Impact

Supply chain compromise in environments where an attacker can both alter the lockfile and cause the referenced registry URL to serve altered package content. The `--frozen-lockfile` flag does not fail closed when the integrity field is missing.

## Suggested Remediation

Require an `integrity` field for remote tarball resolutions. Change the `if (integrity)` guard to fail when integrity is absent for non-local packages. When `--frozen-lockfile` is active, reject lockfile entries that lack integrity for remote packages.

---

> Discovered by [AutoFyn](https://github.com/SignalPilot-Labs/AutoFyn)
> Full audit report: [audit_report.md](https://github.com/tempcollab/pnpm/blob/main/autofyn_audit/audit_report.md)
> Exploit script: [exploit.sh](https://github.com/tempcollab/pnpm/blob/main/autofyn_audit/exploits/vuln1_integrity_bypass/exploit.sh)

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-q6j5-fjx5-2mc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-50021
- https://github.com/pnpm/pnpm
