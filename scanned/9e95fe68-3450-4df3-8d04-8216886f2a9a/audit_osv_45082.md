# [H] SiYuan: Encrypted-notebook key-derivation material and wrapped notebook keys disclosed to anonymous readers, enabling offline master-password cracking

## Summary
Severity: High
Advisory: GHSA-8x84-r2ff-h8pq
Aliases: CVE-2026-72801, GO-2026-6392
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-8x84-r2ff-h8pq
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724102025-3bc014c7dc32

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72801](https://nvd.nist.gov/vuln/detail/CVE-2026-72801).

### Summary

Two `CheckAuth`-only endpoints disclose the complete offline attack material for the encrypted-notebook master password, plus the wrapped per-notebook key needed to use it. Both are reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. An unauthenticated remote client can retrieve the Argon2id salt and cost parameters, a verifier that confirms a correct password offline, and the encrypted per-notebook data key reducing the security of every encrypted notebook to the master password's resistance to offline GPU cracking.

### Details

**(1) `POST /api/system/getConf` leaks `NotebookCrypto`.**

`getConf` → `GetMaskedConf()` marshals the full configuration including `NotebookCrypto *conf.NotebookCrypto` (JSON tag `notebookCrypto`, not `-`, so it survives the deep copy). For non-administrators `HideConfSecret()` is applied, which nulls a dozen secret-bearing fields like AI, MCPOAuth, Api, Flashcard, Publish, Repo, Sync, Secrets, Variables, System paths but contains **no reference to `NotebookCrypto`**. `FilterConfByPublishIgnore()` for readers only touches `UILayout`.

The reader therefore receives:

| Field | What it is |
|---|---|
| `MasterSalt` | global Argon2id salt |
| `KDFParams` | Argon2id memory/time/parallelism cost |
| `KEKVerifier` + `VerifierNonce` | AES-GCM-encrypted fixed magic, the in-code comment states it exists for offline master-password verification |
| `KEKMAC` | HMAC-SHA256 of the KEK |

Either `KEKVerifier` or `KEKMAC` is a self-contained offline oracle:

```
KEK = Argon2id(guess, MasterSalt, KDFParams)
correct if AES-GCM-decrypt(KEKVerifier, VerifierNonce) == magic
        or HMAC(KEK) == KEKMAC
```

No server round-trips are required, so there is no rate limiting, lockout, or logging on guesses, and the work is fully GPU-parallelisable.

**(2) `POST /api/notebook/getNotebookConf` leaks the wrapped data key.**

`box.GetConf()` returns the full `BoxConf` including `BoxCrypt.WrappedDEK`, the per-notebook data-encryption key wrapped under the KEK via AES-GCM together with `WrapNonce`. `getNotebookInfo` is the same class. Once (1) yields the master password, the attacker derives the KEK, decrypts `WrappedDEK` to recover the real data-encryption key, and decrypts every `.sy` file in that notebook.

**Why this matters beyond the at-rest threat model.** Storing verifier and KDF material alongside the ciphertext is reasonable against a *local* attacker who already has filesystem access. Serving `MasterSalt` + `KDFParams` + `KEKVerifier` + `WrappedDEK` to an *anonymous remote reader* converts that at-rest assumption into a remote pre-authentication cracking opportunity.

**Guarded-sibling asymmetry.** `HideConfSecret` nulls a dozen secret fields but omits `NotebookCrypto`. `lsNotebooks` filters notebook visibility for readers, while `getNotebookConf` and `getNotebookInfo` apply no reader filter at all.

Verified at `origin/master` (`eef105683`): handler bodies as described; `HideConfSecret` contains zero `NotebookCrypto` matches; `FilterConfByPublishIgnore` touches only `UILayout`; all relevant struct JSON tags are non-`-`; all three routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808) with at least one encrypted notebook configured; anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account.

**1. Retrieve the key-derivation material as an anonymous reader:**
```
POST http://127.0.0.1:6808/api/system/getConf
{}
```
The response's `notebookCrypto` object contains `MasterSalt`, `KDFParams`, `KEKVerifier`, `VerifierNonce`, and `KEKMAC` while the same response has the other secret fields (Api, Repo, Sync, Publish, System paths) correctly blanked, demonstrating the omission.

**2. Retrieve the wrapped notebook key:**
```
POST http://127.0.0.1:6808/api/notebook/getNotebookConf
{"notebook":"<NOTEBOOK_ID>"}
```
The response contains `BoxCrypt.WrappedDEK` and `WrapNonce`.

**3. Offline:** candidate passwords are verified locally against `KEKVerifier`/`KEKMAC` using `MasterSalt` and `KDFParams`, with no further server interaction. A recovered password yields the KEK, which unwraps `WrappedDEK` to the notebook's data-encryption key.

*Verification status:* the leak paths are confirmed by code inspection at `origin/master`. A live end-to-end demonstration requires a build from HEAD with an encrypted notebook enabled; the test instance available predates the encrypted-notebook feature, so no runtime reproduction is claimed here.

### Impact

An unauthenticated remote client (publish mode with auth disabled) or any publish `RoleReader` obtains everything needed to mount an unlimited, unthrottled, GPU-parallel offline attack on the encrypted-notebook master password, plus the wrapped data key to decrypt notebook contents once the password is recovered. The confidentiality of every encrypted notebook then rests solely on master-password entropy against an offline attacker, rather than on the password remaining unknown to remote parties. No rate limiting or detection applies, because guessing occurs entirely off-server.

### Suggested fix

- In `HideConfSecret`, replace `NotebookCrypto` with a minimal `{enabled: bool}` for non-administrators the frontend only needs the enabled flag for the lock UI stripping `MasterSalt`, `KDFParams`, `KEKVerifier`, `VerifierNonce`, and `KEKMAC`.
- Apply reader filtering to `getNotebookConf` and `getNotebookInfo` so `BoxCrypt` (including `WrappedDEK` and `WrapNonce`) is omitted for non-administrator roles.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-8x84-r2ff-h8pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72801
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-encryption-key-material
