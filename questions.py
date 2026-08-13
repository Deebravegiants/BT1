import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = "ExodusOSS/hydra"
# todo: the name of the repository
REPO_NAME = "hydra"

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"

scope_files = [
    # =================================================================================
    # SDK composition, RPC bridges, and lifecycle wiring
    # =================================================================================
    "sdks/headless/src/index.js",
    "sdks/headless/src/api/index.js",
    "sdks/headless/src/api/safe-parse.js",
    "sdks/headless/src/features/keychain-rpc/index.js",
    "sdks/headless/src/features/wallet-rpc/index.js",
    "sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js",
    "sdks/headless/src/migrations/attach.js",
    "sdks/headless/src/plugins/attach.js",
    "sdks/headless/src/unlock-encrypted-storage.js",
    "libraries/browser-extension-rpc/src/index.js",
    "libraries/browser-extension-rpc/src/metadata.js",
    "libraries/browser-extension-rpc/src/port-transport.js",
    "libraries/browser-extension-rpc/src/rpc-manager.js",
    "libraries/browser-extension-rpc/src/runtime-port.js",
    "libraries/sdk-rpc/src/client.ts",
    "libraries/sdk-rpc/src/constants.ts",
    "libraries/sdk-rpc/src/rpc.ts",

    # =================================================================================
    # Wallet lifecycle, authentication, seeds, key custody, and signing
    # =================================================================================
    "features/application/src/modules/application.ts",
    "features/application/src/modules/passphrase-cache.ts",
    "features/application/src/plugins/lifecycle.ts",
    "features/auth-mobile/atoms/auth.js",
    "features/auth-mobile/module/auth.js",
    "features/auth-mobile/module/can-use-device-auth.js",
    "features/auth-mobile/module/bio/bio-auth.android.js",
    "features/auth-mobile/module/bio/bio-auth.ios.js",
    "features/auth-mobile/module/bio/biometry.android.js",
    "features/auth-mobile/module/bio/biometry.ios.js",
    "features/keychain/module/keychain.js",
    "features/keychain/module/create-signer.js",
    "features/keychain/module/memoized-keychain.js",
    "features/keychain/module/validate.js",
    "features/keychain/module/errors.js",
    "features/keychain/module/crypto/cardano.js",
    "features/keychain/module/crypto/ed25519.js",
    "features/keychain/module/crypto/schnorr-z.js",
    "features/keychain/module/crypto/secp256k1.js",
    "features/keychain/module/crypto/seed-id.js",
    "features/keychain/module/crypto/sodium.js",
    "features/keychain/module/crypto/tweak.js",
    "features/wallet/module/index.js",
    "features/wallet/module/utils.js",
    "features/wallet/module/wallet.js",
    "features/wallet/migrations/seed-metadata.js",
    "features/wallet/atoms/primary-seed-id.js",
    "features/wallet/atoms/seed-metadata.js",
    "features/cached-sodium-encryptor/module/cache.ts",
    "features/cached-sodium-encryptor/module/cached-sodium-encryptor.ts",
    "features/cached-sodium-encryptor/module/schemas.ts",
    "features/message-signer/src/module/errors.ts",
    "features/message-signer/src/module/hardware-signer.ts",
    "features/message-signer/src/module/message-signer.ts",
    "features/message-signer/src/module/seed-signer.ts",
    "features/tx-signer/src/module/errors.ts",
    "features/tx-signer/src/module/seed-signer.ts",
    "features/tx-signer/src/module/transaction-signer.ts",
    "features/wallet-accounts/src/module/utils.ts",
    "features/wallet-accounts/src/module/wallet-accounts.ts",

    # =================================================================================
    # Origin trust, account exposure, address derivation, and public key export
    # =================================================================================
    "features/connected-origins/atoms/connected-accounts.js",
    "features/connected-origins/atoms/connected-origins.js",
    "features/connected-origins/module/connections.js",
    "features/address-provider/module/address-cache/index.js",
    "features/address-provider/module/address-cache/memory.js",
    "features/address-provider/module/address-cache/utils.js",
    "features/address-provider/module/address-provider.js",
    "features/address-provider/module/known-addresses.js",
    "features/address-provider/module/utils.js",
    "features/address-provider/module/validation.js",
    "features/public-key-provider/module/index.ts",
    "features/public-key-provider/module/public-key-provider.ts",
    "features/public-key-provider/module/store/formats/storage/legacy.ts",
    "features/public-key-provider/module/store/formats/serialization/index.ts",
    "features/public-key-provider/module/store/formats/serialization/monero-public-key.ts",
    "features/public-key-provider/module/store/formats/serialization/public-key.ts",
    "features/public-key-provider/module/store/formats/serialization/xpub.ts",
    "features/asset-sources/module/asset-sources.ts",
    "features/asset-sources/module/utils.ts",

    # =================================================================================
    # Remote config, feature control, and server-driven behavior
    # =================================================================================
    "features/remote-config/atoms/remote-config.ts",
    "features/remote-config/module/generate-remote-config-url.ts",
    "features/remote-config/module/helpers.ts",
    "features/remote-config/module/index.ts",
    "features/feature-flags/atoms/feature-flag-atoms.js",
    "features/feature-flags/atoms/feature-flags-atom.js",
    "features/feature-flags/atoms/remote-config-feature-flags.js",
    "features/feature-flags/atoms/utils/normalize-remote-config-value.js",
    "features/feature-flags/module/index.js",
    "features/fee-data-monitors/monitor/index.js",
    "features/fees/module/index.js",

    # =================================================================================
    # Encrypted storage, persistence, serialization, and migration surfaces
    # =================================================================================
    "adapters/keystore-mobile/src/index.js",
    "adapters/storage-encrypted/src/index.ts",
    "adapters/storage-encrypted/src/storage.ts",
    "adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts",
    "adapters/storage-mobile/src/storage.ts",
    "adapters/storage-unsafe-desktop/src/index.js",
    "adapters/storage-unsafe-desktop/src/internal.js",
    "adapters/storage-unsafe-desktop/src/utils.js",
    "libraries/browser-extension-adapters/encrypted-storage/index.js",
    "libraries/browser-extension-adapters/seco-storage/index.js",
    "libraries/browser-extension-adapters/session-storage/index.js",
    "libraries/browser-extension-adapters/unsafe-storage/index.js",
    "libraries/deferring-storage/src/index.ts",
    "libraries/deferring-storage/src/storage.ts",
    "libraries/seco-file/src/index.js",
    "libraries/seco-keyval/src/index.js",
    "libraries/seco-rw/src/index.js",
    "libraries/secure-container/src/blob.js",
    "libraries/secure-container/src/buffer.js",
    "libraries/secure-container/src/compressed.js",
    "libraries/secure-container/src/crypto.js",
    "libraries/secure-container/src/file.js",
    "libraries/secure-container/src/header.js",
    "libraries/secure-container/src/index.js",
    "libraries/secure-container/src/metadata.js",
    "libraries/secure-container/src/util.js",
    "libraries/transform-storage/src/index.ts",
    "libraries/transform-storage/src/transform.ts",

    # =================================================================================
    # Network parsing, URL/cookie handling, fetch policy, and untrusted content
    # =================================================================================
    "adapters/fetch-factory/src/fetch-factory.js",
    "adapters/fetch-factory/src/hostname.js",
    "modules/networking-common/src/cookie/deserialize.ts",
    "modules/networking-common/src/cookie/serialize.ts",
    "modules/networking-common/src/cookie/validators.ts",
    "modules/networking-common/src/form/index.ts",
    "modules/networking-common/src/http/index.ts",
    "modules/networking-common/src/url/constants.ts",
    "modules/networking-common/src/url/index.ts",
    "modules/networking-mobile/src/cookie/cookie-jar.ts",
    "modules/networking-mobile/src/http/client.ts",
    "modules/networking-mobile/src/url/url-search-params.ts",
    "modules/networking-mobile/src/url/url.ts",
    "libraries/svg-safe/src/cleanup.mjs",
    "libraries/svg-safe/src/index.mjs",
    "libraries/svg-safe/src/validate.mjs",
]


target_scopes = [
    "Critical. An unprivileged attacker controlling only normal wallet inputs such as a website, dapp origin, deeplink, QR payload, imported backup, or RPC/API request can cause unauthorized transaction or message signing, seed creation/import side effects, or private key / seed material disclosure.",
    "Critical. An unprivileged attacker can bypass lock, passphrase, biometric, approval, or account-selection boundaries and perform wallet actions while the wallet should remain locked or scoped to a different account, origin, or user consent state.",
    "Critical. An unprivileged attacker can break connected-origin, public-key, address-provider, or wallet-account isolation so one origin, request, or account receives addresses, xpubs, signatures, or trust/auto-approve privileges that belong to another.",
    "Critical. An unprivileged attacker can abuse remote-config, RPC bridge, serialization, or storage migration flows to persist attacker-chosen security state, weaken signing or approval controls, or recover encrypted wallet secrets without privileged device or node access.",
    "High. An unprivileged attacker can trigger cross-wallet state confusion, stale seed/account binding, or wrong-account signing/address derivation through cache, migration, persistence, or replayable UI/API flows.",
    "High. An unprivileged attacker can turn untrusted URLs, cookies, fetch inputs, SVG or other rendered content into direct wallet compromise, secret exposure, or wallet-authorized actions outside the intended trust boundary.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one hydra target.

    ```
    target_file format:
    "'File Name: sdks/headless/src/index.js -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact hydra target:

    {target_file}

    Project focus:
    Hydra is the Exodus SDK monorepo. Focus on wallet lifecycle, lock/auth state, seed and key custody, signing, origin permissions, address/xpub exposure, encrypted storage, RPC bridges, remote-config driven behavior, and untrusted content/network inputs that can directly compromise wallet trust boundaries.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact JS/TS symbols when possible.
    * Attacker is unprivileged only: no employee access, no leaked keys, no local filesystem access, no privileged wallet state, no malicious node/peer, no phishing, and no social engineering.
    * Allowed attacker inputs are normal external surfaces: dapp/origin requests, deeplinks, QR or clipboard payloads, imported backups/files, wallet RPC calls, remote config responses, API responses, URL/cookie/header values, and rendered asset/NFT/SVG content.
    * Ignore test files, mock files, docs, generated files, config-only findings, and dependency-only issues.
    * Do not rely on mocked paths, direct atom/store mutation from tests, or impossible operator-only setup.
    * Generate 12 to 16 high-signal questions.
    * At least 70% must target auth bypass, signing authorization, origin/account isolation, storage/serialization, remote-config control, or RPC trust-boundary failures.
    * Every question must be testable by unit test, integration test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Secrets stay secret: seed bytes, private keys, passphrases, cached unlock material, and encrypted storage contents must never become readable or derivable by an unprivileged attacker.
    * Consent is explicit and scoped: signing, account exposure, trust, favorites, auto-approve, and wallet actions must stay bound to the right origin, wallet account, and unlocked state.
    * Locked means locked: no path should sign, export, decrypt, restore, import, or mutate protected wallet state while auth/lock checks should block it.
    * Persisted state is authentic: migrations, serialization, caches, and remote-config-fed state must not let attacker-controlled data cross wallets, escalate privileges, or weaken protections.
    * Untrusted network or rendered content must not become scriptable wallet control or secret disclosure.

    Each question must include:
    1. target function/module;
    2. attacker action;
    3. preconditions;
    4. call sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: unit/integration/fuzz PARAMETERS and assert AUTH_BOUNDARY, SECRET_ISOLATION, ORIGIN_SCOPING, or STORAGE_INTEGRITY.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused hydra exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: no privileged wallet state, no leaked keys, no social engineering, and no malicious node/peer/operator assumptions.
- Reject anything that depends only on test/mock/config/docs/generated files, dependency bugs alone, direct store mutation from tests, or best-practice cleanup without exploitable impact.
- Focus on real wallet compromise paths reachable from ordinary dapp/origin requests, deeplinks, QR/import payloads, remote config or API responses, RPC calls, URL/cookie values, or rendered content.

## Validate
- Trace the exact reachable JS/TS path from the attacker input into auth, signing, storage, origin trust, remote-config, serialization, or RPC logic.
- Check whether existing validation, lock/auth, account scoping, approval, origin binding, or serialization guards already stop it.
- Accept only real unauthorized signing, secret disclosure, auth bypass, privilege persistence, wrong-account/origin access, or direct wallet-compromise behavior.
- Require exact file/function support and a reproducible unit/integration/fuzz/invariant PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching Hydra bounty impact]

### Likelihood Explanation
[Preconditions, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Unit/integration test or fuzz/invariant test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for hydra security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject malicious-node, malicious-peer, operator-only, leaked-key, dependency-only, docs/style, generated-file, test/mock/config-only, self-XSS-only, and purely theoretical issues.
- Reject if the exploit needs victim social engineering, impossible setup, direct store mutation, or unsupported behavior outside normal wallet inputs.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged user, unless the claim proves privilege escalation from an unprivileged path.
- The final impact must map to an in-scope Hydra wallet impact such as unauthorized signing, secret disclosure, auth bypass, trust-boundary bypass, or direct loss of user funds.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks/guards reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: unit PoC, integration test, invariant/fuzz test, or exact manual steps.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can a normal external user trigger this through a real wallet surface without privileged access?
- Does the code actually behave as claimed?
- Is the impact caused by this code, not by a malicious node, peer, website operator privilege, or dependency alone?
- Is the unauthorized signing, disclosure, bypass, or wallet compromise concrete, not hypothetical?
- Would a wallet bounty triager accept the proof?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing checks fail]

## Impact Explanation
[Concrete in-scope impact, severity rationale, and wallet bounty category]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/integration test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for hydra.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-user analogs in auth, signing, origin/account isolation, encrypted storage, remote-config, RPC bridge, URL/cookie parsing, or rendered-content trust boundaries.
- Reject malicious-node/peer/operator analogs, mocked-only paths, dependency-only bugs, and no-impact or self-XSS-only analogs.

## Validate
- Map the bug class to the strongest reachable hydra path.
- Prove root cause with exact file/function support.
- Accept only concrete unauthorized signing, secret disclosure, auth bypass, cross-origin/account privilege bleed, or direct wallet-compromise impact.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt
