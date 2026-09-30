# [?] [vm] fix security vulnerability on token

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-05-07
Source: https://github.com/starcoinorg/starcoin/commit/9c6e9169c2f90dafc293a328ed3a263d87f6c5ac
Type: security-commit

## Details
[vm] fix security vulnerability on token

## Patch
### examples/my_token/module/my_token.move
```diff
@@ -3,14 +3,18 @@ address 0xeae6b71b9583150c1c32bc9500ee5d15:
 module MyToken {
      use 0x0::Libra;
      use 0x0::LibraAccount;
+     use 0x0::Transaction;
 
      struct T { }
 
      public fun issue(amount: u64) {
+         // only specific address can issue the token
+         Transaction::assert(Transaction::sender() == 0xeae6b71b9583150c1c32bc9500ee5d15, 8000);
+
          // register token
-         Libra::register<T>();
+         Libra::register<T>(T{});
 
-         // mint 'amount' tokens and check that the market cap increases appropriately
+         // mint 'amount' tokens
          let coin = Libra::mint<T>(amount);
 
          // create 'Balance<Token>' resource under sender account
```

### vm/functional-tests/tests/testsuite/token/my_token.move
```diff
@@ -11,7 +11,7 @@ module MyToken {
 
     public fun new() {
         Transaction::assert(Transaction::sender() == {{alice}}, 8000);
-        Libra::register<T>();
+        Libra::register<T>(T{});
         // mint 100 coins and check that the market cap increases appropriately
         let old_market_cap = Libra::market_cap<T>();
         let coin = Libra::mint<T>(10000);
```

### vm/functional-tests/tests/testsuite/token/simple_token.move
```diff
@@ -0,0 +1,80 @@
+// Test user-defined token
+//! account: alice
+//! account: bob
+
+//! sender: alice
+
+module Token {
+    use 0x0::Transaction;
+
+    resource struct Coin<AssetType: copyable> {
+        type: AssetType,
+        value: u64,
+    }
+
+    // control the minting/creation in the defining module of `ATy`
+    public fun create<ATy: copyable>(type: ATy, value: u64): Coin<ATy> {
+        Coin { type, value: 0 }
+    }
+
+    public fun value<ATy: copyable>(coin: &Coin<ATy>): u64 {
+        coin.value
+    }
+
+    public fun split<ATy: copyable>(coin: Coin<ATy>, amount: u64): (Coin<ATy>, Coin<ATy>) {
+        let other = withdraw(&mut coin, amount);
+        (coin, other)
+    }
+
+    public fun withdraw<ATy: copyable>(coin: &mut Coin<ATy>, amount: u64): Coin<ATy> {
+        Transaction::assert(coin.value >= amount, 10);
+        coin.value = coin.value - amount;
+        Coin { type: *&coin.type, value: amount }
+    }
+
+    public fun join<ATy: copyable>(coin1: Coin<ATy>, coin2: Coin<ATy>): Coin<ATy> {
+        deposit(&mut coin1, coin2);
+        coin1
+    }
+
+    public fun deposit<ATy: copyable>(coin: &mut Coin<ATy>, check: Coin<ATy>) {
+        let Coin { value, type } = check;
+        Transaction::assert(&coin.type == &type, 42);
+        coin.value = coin.value + value;
+    }
+
+    public fun destroy_zero<ATy: copyable>(coin: Coin<ATy>) {
+        let Coin { value, type: _ } = coin;
+        Transaction::assert(value == 0, 11)
+    }
+
+}
+
+//! new-transaction
+//! sender: bob
+
+module ToddNickles {
+    use {{alice}}::Token;
+    use 0x0::Transaction;
+
+    struct T {}
+
+    resource struct Wallet {
+        nickles: Token::Coin<T>,
+    }
+
+    public fun init() {
+        Transaction::assert(Transaction::sender() == {{bob}}, 42);
+        move_to_sender(Wallet { nickles: Token::create(T{}, 0) })
+    }
+
+    public fun mint(): Token::Coin<T> {
+        Transaction::assert(Transaction::sender() == {{bob}}, 42);
+        Token::create(T{}, 5)
+    }
+
+    public fun destroy(c: Token::Coin<T>) acquires Wallet {
+        Token::deposit(&mut borrow_global_mut<Wallet>({{bob}}).nickles, c)
+    }
+
+}
```

### vm/functional-tests/tests/testsuite/token/token_vulnerability.move
```diff
@@ -0,0 +1,19 @@
+//! account: alice
+
+//! sender: alice
+
+use 0x0::Starcoin;
+use 0x0::Libra;
+use 0x0::LibraAccount;
+use 0x0::Transaction;
+fun main() {
+    let balance_old = LibraAccount::balance<Starcoin::T>(Transaction::sender());
+    Libra::register<Starcoin::T>();
+    let coin = Libra::mint<Starcoin::T>(10000);
+    Transaction::assert(Libra::value<Starcoin::T>(&coin) == 10000, 8001);
+    LibraAccount::deposit_to_sender<Starcoin::T>(coin);
+    let balance_new = LibraAccount::balance<Starcoin::T>(Transaction::sender());
+    Transaction::assert(balance_new == balance_old + 10000, 8003)
+}
+
+// check: MoveSourceCompilerError
```

### vm/stdlib/modules/lbr.move
```diff
@@ -8,6 +8,6 @@ module LBR {
 
     public fun initialize() {
         Transaction::assert(Transaction::sender() == 0xA550C18, 0);
-        Libra::register<T>();
+        Libra::register<T>(T{});
     }
 }
```

### vm/stdlib/modules/libra.move
```diff
@@ -11,7 +11,9 @@ module Libra {
     }
 
     // A singleton resource that grants access to `Libra::mint`. Only the Association has one.
-    resource struct MintCapability<Token> { }
+    resource struct MintCapability<Token> {
+        t: Token,
+    }
 
     resource struct Info<Token> {
         // The sum of the values of all Libra::T resources in the system
@@ -37,10 +39,10 @@ module Libra {
         is_approved: bool,
     }
 
-    public fun register<Token>() {
+    public fun register<Token>(t: Token) {
         // Only callable by the Association address
         // Transaction::assert(Transaction::sender() == 0xA550C18, 1);
-        move_to_sender(MintCapability<Token>{ });
+        move_to_sender(MintCapability<Token>{ t });
         move_to_sender(Info<Token> { total_value: 0u128, preburn_value: 0 });
     }
 
```

### vm/stdlib/modules/starcoin.move
```diff
@@ -8,6 +8,6 @@ module Starcoin {
 
     public fun initialize() {
         Transaction::assert(Transaction::sender() == 0xA550C18, 0);
-        Libra::register<T>();
+        Libra::register<T>(T{});
     }
 }
```
