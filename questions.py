import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'defuse-protocol/sdk-monorepo'
# todo: the name of the repository
REPO_NAME = 'sdk-monorepo'

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
    # LENS: INTENT SIGNING, WITHDRAWAL ROUTING AND FEE ACCOUNTING (NEAR Intents SDK).
    # The SDK turns a caller's request - assetId, amount, destinationAddress, memo,
    # routeConfig, a fee estimation, a signer - into a signed MultiPayload that the
    # intents.near contract executes and a bridge pays out on another chain. The files
    # below sit on the path from those inputs to one of four decisions: does the payload
    # signed equal the payload built, does the amount debited equal amount + fee once,
    # does the address encoded equal the address validated for that chain, and does the
    # bridge chosen custody the token. A question belongs here only if it can be closed
    # by an equality between a value the caller supplied and a value the SDK emitted.
    # =================================================================================
    # -- intents-sdk: the public IntentsSDK facade and every entry point ---------------
    # sdk.ts owns bridge ordering, createWithdrawalIntents, estimateWithdrawalFee,
    # signAndSendIntent / signAndSendWithdrawalIntent, invalidateNonces, the salt retry,
    # waitForWithdrawalCompletion and processWithdrawal.

    # -- intents-sdk: facade, types and constants ------------------------------------------
    "packages/intents-sdk/index.ts",
    "packages/intents-sdk/src/sdk.ts",
    "packages/intents-sdk/src/shared-types.ts",
    "packages/intents-sdk/src/classes/errors.ts",
    "packages/intents-sdk/src/constants/bridge-name-enum.ts",
    "packages/intents-sdk/src/constants/poa-tokens-migrated-to-omni-bridge.ts",
    "packages/intents-sdk/src/constants/public-rpc-urls.ts",
    "packages/intents-sdk/src/constants/route-enum.ts",
    "packages/intents-sdk/src/constants/withdrawal-timing.ts",
    "packages/intents-sdk/src/core/withdrawal-watcher.ts",

    # -- intents-sdk: intent payload build, nonce, salt, hashing, signing and relay --------
    "packages/intents-sdk/src/intents/expirable-nonce.ts",
    "packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts",
    "packages/intents-sdk/src/intents/intent-hash.ts",
    "packages/intents-sdk/src/intents/intent-hashes/erc191.ts",
    "packages/intents-sdk/src/intents/intent-hashes/nep413.ts",
    "packages/intents-sdk/src/intents/intent-hashes/raw-ed25519.ts",
    "packages/intents-sdk/src/intents/intent-hashes/sep53.ts",
    "packages/intents-sdk/src/intents/intent-hashes/tip191.ts",
    "packages/intents-sdk/src/intents/intent-hashes/ton-connect.ts",
    "packages/intents-sdk/src/intents/intent-hashes/webauthn.ts",
    "packages/intents-sdk/src/intents/intent-payload-builder.ts",
    "packages/intents-sdk/src/intents/intent-payload-factory.ts",
    "packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts",
    "packages/intents-sdk/src/intents/intent-signer-impl/factories.ts",
    "packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-near-keypair.ts",
    "packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts",
    "packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-noop.ts",
    "packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-viem.ts",
    "packages/intents-sdk/src/intents/interfaces/intent-executer.ts",
    "packages/intents-sdk/src/intents/interfaces/intent-relayer.ts",
    "packages/intents-sdk/src/intents/interfaces/intent-signer.ts",
    "packages/intents-sdk/src/intents/interfaces/salt-manager.ts",
    "packages/intents-sdk/src/intents/salt-manager.ts",
    "packages/intents-sdk/src/intents/shared-types.ts",

    # -- intents-sdk: bridges - route selection, validation, intent construction, status --
    "packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-constants.ts",
    "packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-utils.ts",
    "packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts",
    "packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-constants.ts",
    "packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts",
    "packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts",
    "packages/intents-sdk/src/bridges/direct-bridge/error.ts",
    "packages/intents-sdk/src/bridges/hot-bridge/error.ts",
    "packages/intents-sdk/src/bridges/hot-bridge/hot-bridge-chains.ts",
    "packages/intents-sdk/src/bridges/hot-bridge/hot-bridge-constants.ts",
    "packages/intents-sdk/src/bridges/hot-bridge/hot-bridge-utils.ts",
    "packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts",
    "packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts",
    "packages/intents-sdk/src/bridges/omni-bridge/error.ts",
    "packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-constants.ts",
    "packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-utils.ts",
    "packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts",
    "packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts",
    "packages/intents-sdk/src/bridges/poa-bridge/errors.ts",
    "packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts",
    "packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts",
    "packages/intents-sdk/src/bridges/poa-bridge/poa-constants.ts",

    # -- intents-sdk: address validation, fee math, asset parsing and helpers -------------
    "packages/intents-sdk/src/lib/array.ts",
    "packages/intents-sdk/src/lib/async.ts",
    "packages/intents-sdk/src/lib/caip2.ts",
    "packages/intents-sdk/src/lib/compareAddresses.ts",
    "packages/intents-sdk/src/lib/configure-rpc-config.ts",
    "packages/intents-sdk/src/lib/estimate-fee.ts",
    "packages/intents-sdk/src/lib/hex.ts",
    "packages/intents-sdk/src/lib/nep413.ts",
    "packages/intents-sdk/src/lib/object.ts",
    "packages/intents-sdk/src/lib/parse-defuse-asset-id.ts",
    "packages/intents-sdk/src/lib/route-config-factory.ts",
    "packages/intents-sdk/src/lib/tokensUsdPricesHttpClient/apis.ts",
    "packages/intents-sdk/src/lib/tokensUsdPricesHttpClient/index.ts",
    "packages/intents-sdk/src/lib/tokensUsdPricesHttpClient/types.ts",
    "packages/intents-sdk/src/lib/ton-address.ts",
    "packages/intents-sdk/src/lib/validateAddress.ts",
    "packages/intents-sdk/src/lib/zcash-unified-address.ts",

    # -- internal-utils: identity, signature transforms, payload prep, NEAR/relay clients --
    "packages/internal-utils/src/index.ts",
    "packages/internal-utils/src/config.ts",
    "packages/internal-utils/src/logger.ts",
    "packages/internal-utils/src/nearClient.ts",
    "packages/internal-utils/src/errors/assert.ts",
    "packages/internal-utils/src/errors/base.ts",
    "packages/internal-utils/src/errors/index.ts",
    "packages/internal-utils/src/errors/request.ts",
    "packages/internal-utils/src/errors/utils/isNetworkError.ts",
    "packages/internal-utils/src/errors/utils/toError.ts",
    "packages/internal-utils/src/services/blockchainBalanceService.ts",
    "packages/internal-utils/src/types/authHandle.ts",
    "packages/internal-utils/src/types/base.ts",
    "packages/internal-utils/src/types/intentsUserId.ts",
    "packages/internal-utils/src/types/walletMessage.ts",
    "packages/internal-utils/src/types/webAuthn.ts",
    "packages/internal-utils/src/utils/abortSignal.ts",
    "packages/internal-utils/src/utils/appFee.ts",
    "packages/internal-utils/src/utils/assert.ts",
    "packages/internal-utils/src/utils/authIdentity.ts",
    "packages/internal-utils/src/utils/failover.ts",
    "packages/internal-utils/src/utils/handleResponse.ts",
    "packages/internal-utils/src/utils/handleRPCResponse.ts",
    "packages/internal-utils/src/utils/index.ts",
    "packages/internal-utils/src/utils/messageFactory.ts",
    "packages/internal-utils/src/utils/multiPayload/webauthn.ts",
    "packages/internal-utils/src/utils/near.ts",
    "packages/internal-utils/src/utils/poll.ts",
    "packages/internal-utils/src/utils/prepareBroadcastRequest.ts",
    "packages/internal-utils/src/utils/promise/withTimeout.ts",
    "packages/internal-utils/src/utils/request.ts",
    "packages/internal-utils/src/utils/requestShouldRetry.ts",
    "packages/internal-utils/src/utils/retry.ts",
    "packages/internal-utils/src/utils/rpc-endpoint.ts",
    "packages/internal-utils/src/utils/serialize.ts",
    "packages/internal-utils/src/utils/stellarAddressToBytes.ts",
    "packages/internal-utils/src/utils/token.ts",
    "packages/internal-utils/src/utils/tokenUtils.ts",
    "packages/internal-utils/src/utils/tronAddressToHex.ts",
    "packages/internal-utils/src/utils/uint8Array.ts",
    "packages/internal-utils/src/utils/wait.ts",
    "packages/internal-utils/src/utils/webAuthn.ts",

    # -- internal-utils: solver relay - quotes, publish, settlement -----------------------
    "packages/internal-utils/src/solverRelay/index.ts",
    "packages/internal-utils/src/solverRelay/errors/intentSettlement.ts",
    "packages/internal-utils/src/solverRelay/errors/quote.ts",
    "packages/internal-utils/src/solverRelay/getQuote.ts",
    "packages/internal-utils/src/solverRelay/getStatus.ts",
    "packages/internal-utils/src/solverRelay/publishIntent.ts",
    "packages/internal-utils/src/solverRelay/publishIntents.ts",
    "packages/internal-utils/src/solverRelay/solverRelayHttpClient/apis.ts",
    "packages/internal-utils/src/solverRelay/solverRelayHttpClient/index.ts",
    "packages/internal-utils/src/solverRelay/solverRelayHttpClient/runtime.ts",
    "packages/internal-utils/src/solverRelay/solverRelayHttpClient/types.ts",
    "packages/internal-utils/src/solverRelay/types/quote.ts",
    "packages/internal-utils/src/solverRelay/utils/parseFailedPublishError.ts",
    "packages/internal-utils/src/solverRelay/utils/quoteWithLog.ts",
    "packages/internal-utils/src/solverRelay/waitForIntentSettlement.ts",

    # -- internal-utils: PoA bridge, bridge indexer and XRPL clients ----------------------
    "packages/internal-utils/src/poaBridge/index.ts",
    "packages/internal-utils/src/poaBridge/constants/blockchains.ts",
    "packages/internal-utils/src/poaBridge/errors/withdrawal.ts",
    "packages/internal-utils/src/poaBridge/getPendingDeposits.ts",
    "packages/internal-utils/src/poaBridge/poaBridgeHttpClient/apis.ts",
    "packages/internal-utils/src/poaBridge/poaBridgeHttpClient/index.ts",
    "packages/internal-utils/src/poaBridge/poaBridgeHttpClient/runtime.ts",
    "packages/internal-utils/src/poaBridge/poaBridgeHttpClient/types.ts",
    "packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts",
    "packages/internal-utils/src/bridgeIndexer/index.ts",
    "packages/internal-utils/src/bridgeIndexer/bridgeIndexerHttpClient/apis.ts",
    "packages/internal-utils/src/bridgeIndexer/bridgeIndexerHttpClient/index.ts",
    "packages/internal-utils/src/bridgeIndexer/bridgeIndexerHttpClient/runtime.ts",
    "packages/internal-utils/src/bridgeIndexer/bridgeIndexerHttpClient/types.ts",
    "packages/internal-utils/src/xrpl/index.ts",
    "packages/internal-utils/src/xrpl/xrplHttpClient/apis.ts",
    "packages/internal-utils/src/xrpl/xrplHttpClient/errors.ts",
    "packages/internal-utils/src/xrpl/xrplHttpClient/index.ts",
    "packages/internal-utils/src/xrpl/xrplHttpClient/runtime.ts",
    "packages/internal-utils/src/xrpl/xrplHttpClient/types.ts",

    # -- crosschain-assetid: 1cs asset id parse / stringify ----------------------------------
    "packages/crosschain-assetid/src/index.ts",
    "packages/crosschain-assetid/src/parse.ts",
    "packages/crosschain-assetid/src/stringify.ts",
    "packages/crosschain-assetid/src/types.ts",
    "packages/crosschain-assetid/src/uniswap.ts",

    # -- contract-types: the hand-written Standard Schema adapter over generated schemas ----
    "packages/contract-types/src/standard-schema.ts",

    # =================================================================================
    # NOT AUDITED (excluded from every variant): *.test.ts / *.spec.ts / *.integration.test.ts,
    # __snapshots__ and tests/ directories; generated code (contract-types/src/index.ts,
    # validate.ts, type-check-schemas.ts) and the generators that emit it
    # (contract-types/scripts/gen-defuse-types.ts, crosschain-assetid/src/gen.ts); every
    # tsdown.config.ts, biome / turbo / vitest / tsconfig, package.json and pnpm files;
    # .changeset, CHANGELOG and README. A defect in any of these is only in scope when it
    # is reachable from the audited code above.
    # =================================================================================
]


target_scopes = [
    "Critical. THE BYTES SIGNED MUST EQUAL THE PAYLOAD THE CALLER BUILT. `IntentExecuter.signAndSendIntent` builds through `defaultIntentPayloadFactory`, then `mergeIntentPayloads` spreads `customPayload` over `basePayload`, dedupes intents with `new Set([...])` (reference identity, not value), strips `nonce` and re-encodes it with `nonceDeadline = deadline + DEFAULT_NONCE_DEADLINE_OFFSET_MS`; `IntentPayloadBuilder.buildWithSalt` honours `customNonce`, `customRandomBytes` and `setVerifyingContract`; `IntentSignerNEP413.signIntent` serialises only `deadline`, `intents`, `signer_id` into `message` with `recipient = verifying_contract`; `IntentSignerViem.signIntent` serialises all five fields. Probe every field that can differ between what the caller passed and what the wallet signs: a value-duplicate `ft_withdraw` surviving the Set so the user pays twice; a factory returning `intents: undefined` merged with base intents in another order; a `verifying_contract` override signed for another contract; `signer_id` falling back to `accountId` or the derived EVM id; a `deadline` string the caller never produced parsed by `new Date(params.deadline)`. Identity: (signer_id, verifying_contract, deadline, nonce, intents) in the signed `MultiPayload` == the values the caller supplied, with `intents.length` equal to the number of distinct intents.",

    "Critical. THE INTENT AMOUNT MUST EQUAL REQUESTED PLUS FEE, COUNTED ONCE. `IntentsSDK.createWithdrawalIntents` computes `actualAmount = amount - feeEstimation.amount` when `feeInclusive` with no `FeeExceedsAmountError` guard (only `_estimateWithdrawalFee` has it); `PoaBridge.createWithdrawalIntents` adds `relayerFee` back; `deriveOmniWithdrawIntentParams` adds `utxoMaxGasFee + utxoProtocolFee` for UTXO chains and emits `MaxGasFee`; `HotBridge.createWithdrawalIntents` adds `feeAmount` only when `native`; every bridge prepends a `token_diff` from `feeEstimation.quote`; `signAndSendWithdrawalIntent` pairs `zip(withdrawalParamsArray, feeEstimations)` and pushes every `fee.quote.quote_hash`. Show a withdrawal where the user's balance moves by a different amount than requested plus displayed fee: a caller-supplied `feeEstimation` from another asset or route accepted because `getUnderlyingFee` only checks the route key; a negative `actualAmount` serialised as a `\"-N\"` string; a batch where `zip` pairs fee i with params j; a UTXO withdrawal where fees are subtracted then re-added; a `token_diff` whose `amount_in` no longer matches the `quote_hash` sent. Identity: sum of debits across the produced intents == `withdrawalParams.amount` (plus `feeEstimation.amount` when not fee-inclusive), and the destination receives exactly the amount the caller was shown.",

    "Critical. THE ADDRESS ENCODED INTO THE INTENT MUST BE THE ADDRESS VALIDATED FOR THAT CHAIN. `validateAddress` gates every route, then the bridge encodes the raw string: PoA `createWithdrawMemo` builds `WITHDRAW_TO:<address>[:<memo>]` and strips `bitcoincash:`; Omni lowercases `bc1` and wraps with `omniAddress`; HOT passes `receiver` to `buildGaslessWithdrawIntent`; Aurora `makeAuroraEngineDepositMsg` uses `getAddress`; Direct and Intents routes use `receiver_id` verbatim. Probe every accept-set gap: `validateLitecoinAddress` accepting `3...` Bitcoin P2SH; `validateDogeAddress`, `validateStellarAddress`, `validateSuiAddress`, `validateStarknetAddress` and the legacy branch of `validateBchAddress` regex-only with no checksum; `validateMovementAddress` padding short hex; a `destinationMemo` or address containing `:` that splits the PoA memo; an XRPL X-address carrying its own tag next to `destinationMemo`; the `requireDestinationTag` check skipped when `getAccountInfo` throws for a non-XRP asset; a TON raw address with an out-of-range workchain; `compareAddresses` returning false on malformed input so the token-address block is bypassed. Identity: the (chain, address, memo) the bridge pays out to == the (chain, address, memo) the user passed and `validateAddress` approved.",

    "Critical. THE BRIDGE CHOSEN MUST BE THE CONTRACT THAT CUSTODIES THE TOKEN. `IntentsSDK.bridges` is ordered `IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge` and the first `supports()` wins. `PoaBridge.parseAssetId` matches `endsWith('.' + poaTokenFactoryContractID)` and `contractIdToCaip2` by `prefix.` / `prefix-`; `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE` flips PoA tokens to Omni; `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and resolves the destination token through `getBridgedToken`; `HotBridge.parseAssetId` keys on `GlobalSettings.omniHotContract`; `DirectBridge` accepts every nep141 and forwards `routeConfig.msg` into `ft_withdraw` so `ft_transfer_call` runs on the recipient; `IntentsBridge` builds `transfer` to any `receiver_id`. Show a token routed to a bridge that does not hold it or to a chain the user did not name: a contract id under the PoA factory with an unknown prefix; a migrated token whose `poaContractIdToChainKind` differs from its origin chain; `createOmniBridgeRoute(chain)` sending a token to a chain where `getBridgedToken` returns a different asset; a `msg` reaching an arbitrary NEAR contract through the Direct route; a `routeConfig` that makes one bridge throw and silently falls through to the next. Identity: the `receiver_id` / `recipient` / chain of the produced intent == the bridge contract and chain that custodies `assetId`.",

    "High. ONE SIGNED PAYLOAD MUST EXECUTE ONCE, ON ONE CONTRACT. `VersionedNonceBuilder.encodeNonce` packs `salt(4) | deadline u64 LE | random(15)`; `createTimestampedNonceBytes` leaves only 7 random bytes; `decodeNonce` reads `bytes[4]` as version without checking it; `SaltManager` caches `current_salt` for `SALT_TTL_MS` and `withSaltRetry` re-signs and re-publishes on `INVALID_SALT`; `invalidateNonces` signs an empty intent with `deadline = min(now + 1 min, nonce deadline)` and relies on relayer in-memory invalidation; `IntentPayloadBuilder.setNonce` accepts any string. Show a signature that executes twice, executes after the caller believes it dead, or is accepted for a different contract or chain: a nonce collision from 7 random bytes; an invalidation whose deadline lands after the original intent's deadline so it does nothing; a retry after `INVALID_SALT` that publishes a second, differently-nonced payload while the first was accepted; a nonce with a wrong version byte the contract treats as a legacy 32-byte nonce; a NEP-413 `recipient` that differs from the `verifying_contract` the caller intended. Identity: number of on-chain executions per `MultiPayload` == 1, and the (nonce, verifying_contract) pair binds it to exactly one contract on one chain.",

    "High. THE LOCALLY COMPUTED INTENT HASH MUST EQUAL THE CONTRACT'S. `computeIntentHash` is what `onBeforePublishIntent` hands integrators to persist and later match against `waitForIntentSettlement`; `computeTonConnectHash` encodes `domain.length` (UTF-16 units) beside `TextEncoder` bytes and packs `timestamp` with `numberToBigEndian` using 32-bit `>>=`; `computeSignedNep413Hash` rebuilds through `hashNEP413Message` from `payload.nonce` and `callbackUrl`; ERC-191 and TIP-191 prefix `data.length`; `computeWebAuthnHash` hashes only `payload`. Show a payload whose local hash differs from the hash the relayer returns so the integrator tracks the wrong intent, retries, or double-sends: a non-ASCII TON domain, a timestamp above 2^31, a NEP-413 payload with `callbackUrl` set, a `signature` string that `signRaw` re-encodes. Identity: `computeIntentHash(multiPayload)` == the `intent_hash` returned by `publishIntent` for the same payload, for every `standard`.",

    "High. THE SIGNER ID MUST BE THE ACCOUNT THE VERIFYING KEY CONTROLS. `authHandleToIntentsUserId` lowercases EVM and NEAR ids, hex-encodes Solana and Stellar keys, keccaks P-256 WebAuthn keys, trusts a 64-hex TON id and maps Tron as `0x${hex.substring(2)}`; `prepareSwapSignedData` derives `public_key` from `userInfo.userAddress` for raw_ed25519, sep53 and ton_connect rather than from the signature; `IntentSignerViem.signIntent` picks `intent.signer_id ?? accountId ?? derived address`; `transformERC191Signature` normalises `v` via `toRecoveryBit`; `IntentSignerNEP413.signRaw` re-encodes any signature not starting with `ed25519:`. Show two credentials colliding on one intents user id, or a payload whose `signer_id` names an account the attached key does not control yet leaves the SDK unchanged: a Solana key and a WebAuthn ed25519 key with identical raw bytes; a Tron base58 string whose 21-byte payload has no checksum in `tronAddressToHex`; a Stellar string with a valid CRC but wrong version byte; an EVM `signer_id` set to another user's address with the attacker's key. Identity: `signer_id` in the signed payload == the intents user id derived from the public key that produced `signature`.",

    "Critical. THE STATUS THE SDK REPORTS MUST BE THE OUTCOME ON THE DESTINATION CHAIN. `watchWithdrawal` polls `bridge.describeWithdrawal` per `WithdrawalIdentifier { index, tx }`; `PoaBridge.findMatchingWithdrawal` matches by `assetId` only; `HotBridge.describeWithdrawal` picks `nonces[args.index]` from `parseWithdrawalNonces(tx.hash)` and falls back to `bridge_withdrawal_hash` by nonce; `OmniBridge.describeWithdrawal` indexes `getTransfer()[args.index]` and returns `completed, txHash: null` for unknown chain kinds; `DirectBridge`, `IntentsBridge` and `AuroraEngineBridge` return `completed` unconditionally; `parsePublishIntentsResponse` treats `already processed` as OK; `waitForIntentSettlement` only fails on `NOT_FOUND_OR_NOT_VALID` with `FAILED`. Show a batch or single withdrawal where the reported (status, txHash) belongs to a different withdrawal or to nothing: two withdrawals of one PoA token in one intent; a batch mixing HOT and non-HOT routes where `index` counts all params but `nonces` counts only HOT ones; an Omni transfer list ordered differently from the intents; a `completed` returned for a withdrawal the bridge never executed. Identity: the (status, txHash) returned for withdrawal i == the on-chain outcome of the i-th withdrawal the user signed, so an integrator crediting or refunding on it never pays twice.",

    "High. THE FEE THE USER PAYS MUST EQUAL THE FEE THE SDK DISPLAYED. `getFeeQuote` falls back to an exact-in quote sized from `tokens()` USD prices times 1.2 and accepts up to a 1.5x `amount_out / feeAmount` ratio; `HotBridge.estimateWithdrawalFee` multiplies `gasPrice` by 100 on Plasma; `OmniBridge.estimateWithdrawalFee` folds `storageDepositFee` into the quote while `deriveOmniWithdrawIntentParams` also emits a `storage_deposit` of `nativeFee` for `prefundedNativeFeeTokens` whose `amount` was reported as 0; `FEE_SUBSIDIZED_TOKENS` zero `native_token_fee` after the API returned one; `DirectBridge` and `AuroraEngineBridge` quote `minStorageBalance - userStorageBalance` from cached values; `getQuote.matchesRequest` filters solver quotes. Show a user paying more than `feeEstimation.amount`, or a solver or relayer being handed more than the real cost: a `token_diff` selling `amount_in` for an `amount_out` nobody needs; a fee quoted against the wrong `feeAssetId` on HOT; a storage deposit charged twice; a solver quote that passes `matchesRequest` yet moves a different token amount; a stale cache turning a zero fee into a positive one. Identity: value leaving the user's balance beyond `withdrawalParams.amount` == `feeEstimation.amount`, and nothing above the relayer's real cost is transferred to any party.",

    "Critical. THE MISSING INVARIANT - what nobody built. No check ties the intents `createWithdrawalIntents` produces back to the `feeEstimation` they were built from once the caller passes both in separately; nothing asserts a `MultiPayload` handed to `sendSignedIntents` or `signedIntents.before/after` was built for `envConfig.contractID`; `validateWithdrawal` runs before the bridge mutates the amount for PoA and UTXO routes; `describeWithdrawal` never confirms the address or amount it reports against what was signed; the local `computeIntentHash` is never reconciled with the relayer's returned hash. Identify the FIRST place one of these unstated conservation assumptions is violated by an unprivileged user, a counterparty-supplied string, or a solver quote, prove it with a vitest test that asserts both sides (intents produced versus amount plus fee, address signed versus address validated, hash local versus hash returned, status per index versus signed withdrawal) before and after, and show that no later step in `processWithdrawal` can detect or reverse it.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate intent-signing / withdrawal-routing / fee audit questions for one sdk-monorepo target.

    ```
    target_file format:
    "'File Name: packages/intents-sdk/src/sdk.ts -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate SDK and cross-chain security audit questions for this exact sdk-monorepo
    target:

    {target_file}

    Project focus:
    The NEAR Intents SDK turns a caller's request - assetId, amount, destinationAddress,
    destinationMemo, routeConfig, a fee estimation, a signer - into a signed `MultiPayload`
    that the intents contract executes and a bridge (PoA, Omni, HOT, Direct, Aurora,
    internal transfer) pays out on another chain. Untrusted input enters through the
    strings an integrator forwards from an end user, solver quotes returned through the
    relay, and any pre-built nonce, payload factory or signed intent a caller supplies.
    The system decides (a) whether the payload signed equals the payload built; (b)
    whether the amount debited equals amount plus fee, once; (c) whether the address
    encoded equals the address validated for that chain and the bridge chosen custodies
    the token; (d) whether one signature executes once and the status reported equals
    the on-chain outcome. Anything signed, debited, routed or reported that the caller
    did not ask for is the bug.

    Rules:
    * Treat `File Name:` as the exact file.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact TypeScript symbols (exported function, class method, constant, enum
      member, error class, intent field) as they appear in the file.
    * EVERY question must close on an equality that must hold across a call. State it
      explicitly. Narrative questions with no stated equality are rejected.
    * Attacker is unprivileged only: an ordinary NEAR Intents user with their own funds
      and keys, a counterparty whose strings (assetId, destinationAddress, memo,
      routeConfig, quoteHashes, nonce, signedIntents) an integrator forwards into the
      SDK, or a permissionless solver answering a quote. They may call any public SDK
      method with any arguments and order their own calls.
    * Attacker is NOT the integrator deliberately misusing a documented escape hatch, the
      relayer, an RPC node, a bridge API or indexer operator, or a contract admin. No
      malicious peer, node, RPC or relayer; no compromised dependency or device; no
      social engineering.
    * PROGRAM EXCLUSIONS - a question landing in any of these wastes the whole batch:
      - Tests, snapshots, generated contract-types (index.ts, validate.ts,
        type-check-schemas.ts), the generators, tsdown/biome/turbo config, README and
        CHANGELOG are OUT OF SCOPE.
      - Denial of service, rate limiting, timeouts, unbounded loops, cache growth and
        memory hygiene are OUT OF SCOPE.
      - Trust assumptions about external RPCs, the relayer, bridge APIs and price feeds
        are OUT OF SCOPE; the SDK failing to check what it does receive is IN scope.
      - Defects inside intents.near, the bridge contracts, or third-party SDKs
        (@hot-labs/omni-sdk, @omni-bridge, viem, near-api-js) with no path through this
        repo are OUT OF SCOPE; a weakness here that steers them wrong is fully IN scope.
      - Also excluded: leaked keys, privileged accounts, centralization risk,
        best-practice notes, feature requests, price assumptions, funds sent by mistake
        to a correctly validated address, and theoretical findings.
    * IN-SCOPE IMPACTS - every question must land on one and name it:
      Critical: intent manipulation moving funds the user did not authorise; funds
      delivered to a wrong address, chain or contract with no recovery; a signature
      replayed or executed twice; a fee error that drains a material share of the amount.
      High: a signature bound to the wrong contract, signer or nonce; a withdrawal
      stuck until manual intervention; a status or hash misreport that makes an
      integrator credit or refund twice; a fee overcharge or a solver overpaid.
    * Every question must be a concrete real-world scenario an unprivileged party can
      trigger through the public SDK surface with their own funds and inputs.
    * A thrown error is a finding only when it strands funds already signed for or lets
      an unauthorised debit, route or report through - say which.
    * Generate 40 to 80 high-signal questions.
    * At least 70% must land on a Critical impact rather than a High one.
    * Every question must be testable locally with a vitest test that mocks only HTTP
      (relay, bridge APIs, NEAR RPC). Never propose testing on mainnet or a public
      testnet.
    * Avoid generic checklist questions and repeated root causes.
    * Prefer questions that name TWO values that must be equal and ask whether they are:
      payload signed and payload built, amount debited and amount plus fee, address
      encoded and address validated, bridge chosen and token custodian, executions and
      one, status reported and outcome on chain.

    Known dead ends - do NOT generate questions about these:
    * Anything needing the integrator, relayer, RPC, bridge operator or an admin to act
      maliciously.
    * A bug in intents.near, a bridge contract or a third-party SDK with no path here.
    * DoS, timeouts, memory, logging, or a user harming only their own balance.
    * Findings only reproducible through tests or tooling.

    Core equalities (each question must close on one):
    * SIGNED == BUILT: every field of the signed MultiPayload == what the caller supplied.
    * AMOUNT CONSERVATION: debits across produced intents == amount + fee, counted once.
    * DESTINATION TRUTH: (chain, address, memo) paid == (chain, address, memo) validated.
    * ROUTE TRUTH: bridge contract and chain in the intent == custodian of assetId.
    * SINGLE EXECUTION: executions per signed payload == 1, on one contract, one chain.
    * STATUS TRUTH: (status, txHash) reported for withdrawal i == outcome of withdrawal i.

    Each question must include:
    1. target exported function, class method or constant;
    2. attacker input (the concrete assetId, address, memo, routeConfig, quote, nonce
       or payload fields that matter);
    3. preconditions (route, token, fee-inclusive flag, batch shape, cached state);
    4. call sequence through the SDK, bridge and relayer client;
    5. the equality that breaks, written explicitly;
    6. scoped impact and whose funds are exposed;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Method: function_name] Can an unprivileged ATTACKER_INPUT under PRECONDITIONS trigger CALL_SEQUENCE, breaking the equality EQUALITY, causing scoped impact: SCOPE_IMPACT against PARTY? Proof idea: vitest test PARAMETERS asserting SIGNED_EQUALS_BUILT, AMOUNT_CONSERVATION, DESTINATION_TRUTH, ROUTE_TRUTH, SINGLE_EXECUTION, or STATUS_TRUTH.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate an intent-signing / withdrawal-routing exploit-validation prompt for sdk-monorepo.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an ordinary NEAR Intents user with their own funds and keys, a counterparty whose strings an integrator forwards into the SDK (assetId, destinationAddress, memo, routeConfig, quoteHashes, nonce, signedIntents), or a permissionless solver answering a quote. They may call any public SDK method with any arguments.
- Reject anything requiring the integrator to deliberately misuse a documented escape hatch, a malicious relayer/RPC/bridge API/indexer, a contract admin, a compromised dependency or device, or social engineering.
- OUT OF SCOPE, reject on sight: tests, snapshots, generated contract-types (index.ts, validate.ts, type-check-schemas.ts), generators, tsdown/biome/turbo config, README, CHANGELOG; denial of service, rate limiting, timeouts, unbounded loops, cache growth and memory hygiene; trust assumptions about external RPCs, the relayer, bridge APIs or price feeds; defects inside intents.near, bridge contracts or third-party SDKs with no path through this repo; price assumptions; funds sent by mistake to a correctly validated address; best-practice notes; theoretical findings.
- The impact must be one of: Critical - intent manipulation moving funds the user did not authorise, funds delivered to a wrong address/chain/contract with no recovery, a signature replayed or executed twice, a fee error draining a material share of the amount; High - a signature bound to the wrong contract, signer or nonce, a withdrawal stuck until manual intervention, a status or hash misreport making an integrator credit or refund twice, a fee overcharge or a solver overpaid.
- Focus on real impact: something signed, debited, routed or reported that the caller did not ask for.

## Validate
- Write the equality the question claims is broken between two named values BEFORE tracing any code.
- Trace the exact reachable path from the attacker's input and record every read and write of `intents`, `amount`, `receiver_id` / `recipient` / `memo` / `msg`, `nonce`, `deadline`, `verifying_contract`, `signer_id`, `feeEstimation.amount` / `underlyingFees` / `quote`, and the `WithdrawalIdentifier.index`.
- Evaluate both sides of the equality before and after. If they still match, output no vulnerability.
- Check whether `validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()` ordering, `FeeExceedsAmountError`, `getUnderlyingFee`, `matchesRequest`, the `assert` sanity checks, or the intents contract's own signature and nonce verification already prevent the divergence.
- State what the attacker gains per call and whether it is repeatable.
- Require exact file/function support and a reproducible vitest test that mocks only HTTP.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[The broken equality, the code path, root cause, the attacker's exact input, exploit flow, and why existing guards fail]

### Impact Explanation
[What is signed, debited, misrouted, replayed or misreported, which party, repeatability, matching severity category]

### Likelihood Explanation
[Preconditions, route and token state required, attacker cost, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[vitest test plan with the exact assertions on both sides of the equality]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for sdk-monorepo claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- A claim is only valid if the report states the broken equality between two named values and shows both sides concretely. Reject prose-only claims.
- Reject anything requiring the integrator to deliberately misuse a documented escape hatch, a malicious relayer/RPC/bridge API/indexer, a contract admin, another user's key, a compromised dependency or device, or social engineering.
- OUT OF SCOPE, reject on sight: tests, snapshots, generated contract-types (index.ts, validate.ts, type-check-schemas.ts), generators, tsdown/biome/turbo config, README, CHANGELOG; denial of service, rate limiting, timeouts, unbounded loops, cache growth and memory hygiene; trust assumptions about external RPCs, the relayer, bridge APIs or price feeds; defects inside intents.near, bridge contracts or third-party SDKs with no path through this repo; price assumptions; centralization risk; funds sent by mistake to a correctly validated address; best-practice notes; feature requests; theoretical findings.
- The impact must be one of: Critical - intent manipulation moving funds the user did not authorise, funds delivered to a wrong address/chain/contract with no recovery, a signature replayed or executed twice, a fee error draining a material share of the amount; High - a signature bound to the wrong contract, signer or nonce, a withdrawal stuck until manual intervention, a status or hash misreport making an integrator credit or refund twice, a fee overcharge or a solver overpaid.
- Reject claims where the only loss is the attacker's own balance.
- Reject if the bug was already fixed, publicly disclosed, or covered by a known-issues list.
- A valid report must be triggerable by an unprivileged party against the current code through the public SDK surface.
- A PoC is mandatory. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function/method/constant, and line references.
2. The equality written explicitly, with both sides shown before and after.
3. Clear root cause: which payload-field drift, amount or fee mismatch, address or route gap, nonce or replay error, or status misreport causes it.
4. Reachable exploit path: preconditions -> attacker input -> SDK, bridge and relayer-client sequence -> observed divergence.
5. `validateAddress`, `compareAddresses`, `validateWithdrawal`, bridge `supports()` ordering, `FeeExceedsAmountError`, `getUnderlyingFee`, `matchesRequest` and the contract's own signature and nonce checks reviewed and shown insufficient.
6. Impact stated concretely: which funds, whose, and whether it is repeatable.
7. Reproducible proof: vitest test mocking only HTTP, with the asserted values.

## Silent Triage Questions
Before output, internally answer:
- What exactly is the equality, and does it actually fail?
- Can an ordinary user, forwarded string or solver quote trigger it with no privileged role and no other user's key?
- Is the flaw in this repo's code, not in intents.near, a bridge contract or a third-party SDK?
- What is signed, debited, misrouted, replayed or misreported, whose funds, and can it be repeated?
- Would a HackenProof triager accept the exploit path under the NEAR Intents SDK program?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the broken equality and impact]

## Finding Description
[Exact code path, the equality, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[What is signed, debited, misrouted, replayed or misreported, affected party, repeatability, severity category]

## Likelihood Explanation
[Attacker capability, preconditions, state required, cost, feasibility]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or vitest test plan with concrete assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for sdk-monorepo.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope repo context only (`packages/intents-sdk/src/**`, `packages/internal-utils/src/**`, `packages/crosschain-assetid/src/**` and contract-types/src/standard-schema.ts, excluding tests, generated files and generators). Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged analogs that break an equality: a signed payload field the caller did not supply, an amount debited that is not amount plus fee once, an address or chain paid that was not the one validated, a bridge chosen that does not custody the token, a signature executed twice or on another contract, or a status reported that is not the on-chain outcome.
- OUT OF SCOPE, reject on sight: tests, snapshots, generated contract-types, generators, config, README; denial of service, rate limiting, timeouts, unbounded loops, cache growth and memory hygiene; trust assumptions about external RPCs, the relayer, bridge APIs or price feeds; defects inside intents.near, bridge contracts or third-party SDKs with no path here; anything requiring the integrator, relayer, bridge operator or an admin to act maliciously; malicious peer/node assumptions; price assumptions; funds sent by mistake to a correctly validated address; best-practice notes; theoretical findings.
- The impact must be one of: Critical - intent manipulation moving funds the user did not authorise, funds delivered to a wrong address/chain/contract with no recovery, a signature replayed or executed twice, a fee error draining a material share of the amount; High - a signature bound to the wrong contract, signer or nonce, a withdrawal stuck until manual intervention, a status or hash misreport making an integrator credit or refund twice, a fee overcharge or a solver overpaid.
- Reject analogs where the only loss is the attacker's own balance.

## Validate
- Map the bug class to the strongest reachable path in this repo and state the equality it would break.
- Evaluate both sides before and after the attacker's input.
- Prove root cause with exact file/function support.
- Accept only concrete unauthorised debit, misdelivery, replay, wrong-contract binding, stuck funds, double credit, or overcharge.

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
