[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** third_party/move/tools/move-decompiler/tests/legacy-move-stdlib/vector.exp (L132-148)
```text
    public fun slice<Element: copy>(self: &vector<Element>, start: u64, end: u64): vector<Element> {
        let _v0;
        if (start <= end) {
            let _v1 = length<Element>(self);
            _v0 = end <= _v1
        } else _v0 = false;
        assert!(_v0, 131076);
        let _v2 = empty<Element>();
        while (start < end) {
            let _v3 = &mut _v2;
            let _v4 = *borrow<Element>(self, start);
            push_back<Element>(_v3, _v4);
            start = start + 1;
            continue
        };
        _v2
    }
```

**File:** aptos-move/framework/move-stdlib/src/natives/string.rs (L123-124)
```rust
    let s_str = from_utf8_checked(s_ref.as_slice())?;
    let v = Value::vector_u8(s_str[i..j].as_bytes().iter().cloned());
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L196-197)
```text
        let does_fa_exist = object::object_exists<FAController>(get_fa_obj_address(name, symbol));
        assert!(!does_fa_exist, EFA_EXISTS_ALREADY);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L204-207)
```text
        let fa_key_seed = *string::bytes(&name);
        vector::append(&mut fa_key_seed, b"-");
        vector::append(&mut fa_key_seed, *string::bytes(&symbol));
        let fa_obj_constructor_ref = &object::create_named_object(&fa_generator_signer, fa_key_seed);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L171-174)
```text
        let fa_key_seed = *string::bytes(&name);
        vector::append(&mut fa_key_seed, b"-");
        vector::append(&mut fa_key_seed, *string::bytes(&symbol));
        let liquidity_pair_object = object::create_named_object(&pairs_signer, fa_key_seed);
```
