# [?] Merge pull request #853 from yihuang/fix-overflow

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/cosmwasm
Published: 2021-04-01
Source: https://github.com/CosmWasm/cosmwasm/commit/53a783351e39db4d960746601f1a7a7870fb69d5
Type: security-commit

## Details
Merge pull request #853 from yihuang/fix-overflow

Add methods to UInt128 for explicit overflow control

## Patch
### contracts/staking/src/contract.rs
```diff
@@ -86,8 +86,8 @@ pub fn transfer(
     let sender_raw = deps.api.canonical_address(&info.sender)?;
 
     let mut accounts = balances(deps.storage);
-    accounts.update(&sender_raw, |balance: Option<Uint128>| {
-        balance.unwrap_or_default() - send
+    accounts.update(&sender_raw, |balance: Option<Uint128>| -> StdResult<_> {
+        Ok(balance.unwrap_or_default().checked_sub(send)?)
     })?;
     accounts.update(&rcpt_raw, |balance: Option<Uint128>| -> StdResult<_> {
         Ok(balance.unwrap_or_default() + send)
@@ -209,7 +209,7 @@ pub fn unbond(deps: DepsMut, env: Env, info: MessageInfo, amount: Uint128) -> St
     // deduct all from the account
     let mut accounts = balances(deps.storage);
     accounts.update(&sender_raw, |balance| -> StdResult<_> {
-        balance.unwrap_or_default() - amount
+        Ok(balance.unwrap_or_default().checked_sub(amount)?)
     })?;
     if tax > Uint128(0) {
         // add tax to the owner
@@ -223,14 +223,14 @@ pub fn unbond(deps: DepsMut, env: Env, info: MessageInfo, amount: Uint128) -> St
     let bonded = get_bonded(&deps.querier, &env.contract.address)?;
 
     // calculate how many native tokens this is worth and update supply
-    let remainder = (amount - tax)?;
+    let remainder = amount.checked_sub(tax)?;
     let mut totals = total_supply(deps.storage);
     let mut supply = totals.load()?;
     // TODO: this is just temporary check - we should use dynamic query or have a way to recover
     assert_bonds(&supply, bonded)?;
     let unbond = remainder.multiply_ratio(bonded, supply.issued);
-    supply.bonded = (bonded - unbond)?;
-    supply.issued = (supply.issued - remainder)?;
+    supply.bonded = bonded.checked_sub(unbond)?;
+    supply.issued = supply.issued.checked_sub(remainder)?;
     supply.claims += unbond;
     totals.save(&supply)?;
 
@@ -273,15 +273,15 @@ pub fn claim(deps: DepsMut, env: Env, info: MessageInfo) -> StdResult<Response>
     // check how much to send - min(balance, claims[sender]), and reduce the claim
     let sender_raw = deps.api.canonical_address(&info.sender)?;
     let mut to_send = balance.amount;
-    claims(deps.storage).update(sender_raw.as_slice(), |claim| {
+    claims(deps.storage).update(sender_raw.as_slice(), |claim| -> StdResult<_> {
         let claim = claim.ok_or_else(|| StdError::generic_err("no claim for this address"))?;
         to_send = to_send.min(claim);
-        claim - to_send
+        Ok(claim.checked_sub(to_send)?)
     })?;
 
     // update total supply (lower claim)
     total_supply(deps.storage).update(|mut supply| -> StdResult<_> {
-        supply.claims = (supply.claims - to_send)?;
+        supply.claims = supply.claims.checked_sub(to_send)?;
         Ok(supply)
     })?;
 
@@ -353,15 +353,15 @@ pub fn _bond_all_tokens(
     // we deduct pending claims from our account balance before reinvesting.
     // if there is not enough funds, we just return a no-op
     match total_supply(deps.storage).update(|mut supply| {
-        balance.amount = (balance.amount - supply.claims)?;
+        balance.amount = balance.amount.checked_sub(supply.claims)?;
         // this just triggers the "no op" case if we don't have min_withdrawal left to reinvest
-        (balance.amount - invest.min_withdrawal)?;
+        balance.amount.checked_sub(invest.min_withdrawal)?;
         supply.bonded += balance.amount;
         Ok(supply)
     }) {
         Ok(_) => {}
         // if it is below the minimum, we do a no-op (do not revert other state from withdrawal)
-        Err(StdError::Underflow { .. }) => return Ok(Response::default()),
+        Err(StdError::Overflow(_)) => return Ok(Response::default()),
         Err(e) => return Err(e.into()),
     }
 
@@ -739,7 +739,7 @@ mod tests {
         let res = execute(deps.as_mut(), mock_env(), info, unbond_msg);
         match res.unwrap_err() {
             StakingError::Std {
-                original: StdError::Underflow { .. },
+                original: StdError::Overflow(_),
             } => {}
             err => panic!("Unexpected error: {:?}", err),
         }
```

### packages/std/src/errors/mod.rs
```diff
@@ -4,6 +4,6 @@ mod system_error;
 mod verification_error;
 
 pub use recover_pubkey_error::RecoverPubkeyError;
-pub use std_error::{StdError, StdResult};
+pub use std_error::{DivideByZeroError, OverflowError, OverflowOperation, StdError, StdResult};
 pub use system_error::SystemError;
 pub use verification_error::VerificationError;
```

### packages/std/src/errors/std_error.rs
```diff
@@ -1,5 +1,6 @@
 #[cfg(feature = "backtraces")]
 use std::backtrace::Backtrace;
+use std::fmt;
 use thiserror::Error;
 
 use crate::errors::{RecoverPubkeyError, VerificationError};
@@ -82,13 +83,10 @@ pub enum StdError {
         #[cfg(feature = "backtraces")]
         backtrace: Backtrace,
     },
-    #[error("Cannot subtract {subtrahend} from {minuend}")]
-    Underflow {
-        minuend: String,
-        subtrahend: String,
-        #[cfg(feature = "backtraces")]
-        backtrace: Backtrace,
-    },
+    #[error(transparent)]
+    Overflow(#[from] OverflowError),
+    #[error(transparent)]
+    DivideByZero(#[from] DivideByZeroError),
 }
 
 impl StdError {
@@ -167,15 +165,6 @@ impl StdError {
             backtrace: Backtrace::capture(),
         }
     }
-
-    pub fn underflow<U: ToString>(minuend: U, subtrahend: U) -> Self {
-        StdError::Underflow {
-            minuend: minuend.to_string(),
-            subtrahend: subtrahend.to_string(),
-            #[cfg(feature = "backtraces")]
-            backtrace: Backtrace::capture(),
-        }
-    }
 }
 
 impl PartialEq<StdError> for StdError {
@@ -331,20 +320,16 @@ impl PartialEq<StdError> for StdError {
                     false
                 }
             }
-            StdError::Underflow {
-                minuend,
-                subtrahend,
-                #[cfg(feature = "backtraces")]
-                    backtrace: _,
-            } => {
-                if let StdError::Underflow {
-                    minuend: rhs_minuend,
-                    subtrahend: rhs_subtrahend,
-                    #[cfg(feature = "backtraces")]
-                        backtrace: _,
-                } = rhs
-                {
-                    minuend == rhs_minuend && subtrahend == rhs_subtrahend
+            StdError::Overflow(err) => {
+                if let StdError::Overflow(rhs_err) = rhs {
+                    err == rhs_err
+                } else {
+                    false
+                }
+            }
+            StdError::DivideByZero(err) => {
+                if let StdError::DivideByZero(rhs_err) = rhs {
+                    err == rhs_err
                 } else {
                     false
                 }
@@ -384,6 +369,60 @@ impl From<RecoverPubkeyError> for StdError {
 /// result/error type in cosmwasm-std.
 pub type StdResult<T> = core::result::Result<T, StdError>;
 
+#[derive(Error, Debug, PartialEq, Eq)]
+pub enum OverflowOperation {
+    Add,
+    Sub,
+    Mul,
+    Pow,
+}
+
+impl fmt::Display for OverflowOperation {
+    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+        write!(f, "{:?}", self)
+    }
+}
+
+#[derive(Error, Debug, PartialEq, Eq)]
+#[error("Cannot {operation} with {operand1} and {operand2}")]
+pub struct OverflowError {
+    pub operation: OverflowOperation,
+    pub operand1: String,
+    pub operand2: String,
+    #[cfg(feature = "backtraces")]
+    backtrace: Backtrace,
+}
+
+impl OverflowError {
+    pub fn new<U: ToString>(operation: OverflowOperation, operand1: U, operand2: U) -> Self {
+        Self {
+            operation,
+            operand1: operand1.to_string(),
+            operand2: operand2.to_string(),
+            #[cfg(feature = "backtraces")]
+            backtrace: Backtrace::capture(),
+        }
+    }
+}
+
+#[derive(Error, Debug, PartialEq, Eq)]
+#[error("Cannot devide {operand} by zero")]
+pub struct DivideByZeroError {
+    pub operand: String,
+    #[cfg(feature = "backtraces")]
+    backtrace: Backtrace,
+}
+
+impl DivideByZeroError {
+    pub fn new<U: ToString>(operand: U) -> Self {
+        Self {
+            operand: operand.to_string(),
+            #[cfg(feature = "backtraces")]
+            backtrace: Backtrace::capture(),
+        }
+    }
+}
+
 #[cfg(test)]
 mod tests {
     use super::*;
@@ -513,58 +552,60 @@ mod tests {
 
     #[test]
     fn underflow_works_for_u128() {
-        let error = StdError::underflow(123u128, 456u128);
+        let error = StdError::from(OverflowError::new(OverflowOperation::Sub, 123u128, 456u128));
         match error {
-            StdError::Underflow {
-                minuend,
-                subtrahend,
+            StdError::Overflow(OverflowError {
+                operation: OverflowOperation::Sub,
+                operand1,
+                operand2,
                 ..
-            } => {
-                assert_eq!(minuend, "123");
-                assert_eq!(subtrahend, "456");
+            }) => {
+                assert_eq!(operand1, "123");
+                assert_eq!(operand2, "456");
             }
             _ => panic!("expect different error"),
         }
     }
 
     #[test]
     fn underflow_works_for_i64() {
-        let error = StdError::underflow(777i64, 1234i64);
+        let error = StdError::from(OverflowError::new(OverflowOperation::Sub, 777i64, 1234i64));
         match error {
-            StdError::Underflow {
-                minuend,
-                subtrahend,
+            StdError::Overflow(OverflowError {
+                operation: OverflowOperation::Sub,
+                operand1,
+                operand2,
                 ..
-            } => {
-                assert_eq!(minuend, "777");
-                assert_eq!(subtrahend, "1234");
+            }) => {
+                assert_eq!(operand1, "777");
+                assert_eq!(operand2, "1234");
             }
             _ => panic!("expect different error"),
         }
     }
 
     #[test]
     fn implements_debug() {
-        let error: StdError = StdError::underflow(3, 5);
+        let error: StdError = StdError::from(OverflowError::new(OverflowOperation::Sub, 3, 5));
         let embedded = format!("Debug message: {:?}", error);
         assert_eq!(
             embedded,
-            r#"Debug message: Underflow { minuend: "3", subtrahend: "5" }"#
+            r#"Debug message: Overflow(OverflowError { operation: Sub, operand1: "3", operand2: "5" })"#
         );
     }
 
     #[test]
     fn implements_display() {
-        let error: StdError = StdError::underflow(3, 5);
+        let error: StdError = StdError::from(OverflowError::new(OverflowOperation::Sub, 3, 5));
         let embedded = format!("Display message: {}", error);
-        assert_eq!(embedded, "Display message: Cannot subtract 5 from 3");
+        assert_eq!(embedded, "Display message: Cannot Sub with 3 and 5");
     }
 
     #[test]
     fn implements_partial_eq() {
-        let u1 = StdError::underflow(3, 5);
-        let u2 = StdError::underflow(3, 5);
-        let u3 = StdError::underflow(3, 7);
+        let u1 = StdError::from(OverflowError::new(OverflowOperation::Sub, 3, 5));
+        let u2 = StdError::from(OverflowError::new(OverflowOperation::Sub, 3, 5));
+        let u3 = StdError::from(OverflowError::new(OverflowOperation::Sub, 3, 7));
         let s1 = StdError::serialize_err("Book", "Content too long");
         let s2 = StdError::serialize_err("Book", "Content too long");
         let s3 = StdError::serialize_err("Book", "Title too long");
```

### packages/std/src/lib.rs
```diff
@@ -26,7 +26,10 @@ pub use crate::addresses::{CanonicalAddr, HumanAddr};
 pub use crate::binary::Binary;
 pub use crate::coins::{coin, coins, has_coins, Coin};
 pub use crate::deps::{Deps, DepsMut, OwnedDeps};
-pub use crate::errors::{RecoverPubkeyError, StdError, StdResult, SystemError, VerificationError};
+pub use crate::errors::{
+    OverflowError, OverflowOperation, RecoverPubkeyError, StdError, StdResult, SystemError,
+    VerificationError,
+};
 #[cfg(feature = "stargate")]
 pub use crate::ibc::{
     ChannelResponse, IbcAcknowledgement, IbcBasicResponse, IbcChannel, IbcEndpoint, IbcMsg,
```

### packages/std/src/math.rs
```diff
@@ -6,7 +6,7 @@ use std::iter::Sum;
 use std::ops;
 use std::str::FromStr;
 
-use crate::errors::{StdError, StdResult};
+use crate::errors::{DivideByZeroError, OverflowError, OverflowOperation, StdError};
 
 /// A fixed-point decimal value with 18 fractional digits, i.e. Decimal(1_000_000_000_000_000_000) == 1.0
 ///
@@ -180,6 +180,80 @@ impl Uint128 {
     pub fn is_zero(&self) -> bool {
         self.0 == 0
     }
+
+    pub fn checked_add(self, other: Self) -> Result<Self, OverflowError> {
+        self.0
+            .checked_add(other.0)
+            .map(Self)
+            .ok_or_else(|| OverflowError::new(OverflowOperation::Add, self, other))
+    }
+
+    pub fn checked_sub(self, other: Self) -> Result<Self, OverflowError> {
+        self.0
+            .checked_sub(other.0)
+            .map(Self)
+            .ok_or_else(|| OverflowError::new(OverflowOperation::Sub, self, other))
+    }
+
+    pub fn checked_mul(self, other: Self) -> Result<Self, OverflowError> {
+        self.0
+            .checked_mul(other.0)
+            .map(Self)
+            .ok_or_else(|| OverflowError::new(OverflowOperation::Mul, self, other))
+    }
+
+    pub fn checked_div(self, other: Self) -> Result<Self, DivideByZeroError> {
+        self.0
+            .checked_div(other.0)
+            .map(Self)
+            .ok_or_else(|| DivideByZeroError::new(self))
+    }
+
+    pub fn checked_div_euclid(self, other: Self) -> Result<Self, DivideByZeroError> {
+        self.0
+            .checked_div_euclid(other.0)
+            .map(Self)
+            .ok_or_else(|| DivideByZeroError::new(self))
+    }
+
+    pub fn checked_rem(self, other: Self) -> Result<Self, DivideByZeroError> {
+        self.0
+            .checked_rem(other.0)
+            .map(Self)
+            .ok_or_else(|| DivideByZeroError::new(self))
+    }
+
+    pub fn wrapping_add(self, other: Self) -> Self {
+        Self(self.0.wrapping_add(other.0))
+    }
+
+    pub fn wrapping_sub(self, other: Self) -> Self {
+        Self(self.0.wrapping_sub(other.0))
+    }
+
+    pub fn wrapping_mul(self, other: Self) -> Self {
+        Self(self.0.wrapping_mul(other.0))
+    }
+
+    pub fn wrapping_pow(self, other: u32) -> Self {
+        Self(self.0.wrapping_pow(other))
+    }
+
+    pub fn saturating_add(self, other: Self) -> Self {
+        Self(self.0.saturating_add(other.0))
+    }
+
+    pub fn saturating_sub(self, other: Self) -> Self {
+        Self(self.0.saturating_sub(other.0))
+    }
+
+    pub fn saturating_mul(self, other: Self) -> Self {
+        Self(self.0.saturating_mul(other.0))
+    }
+
+    pub fn saturating_pow(self, other: u32) -> Self {
+        Self(self.0.saturating_pow(other))
+    }
 }
 
 // `From<u{128,64,32,16,8}>` is implemented manually instead of
@@ -250,46 +324,27 @@ impl ops::Add<Uint128> for Uint128 {
     type Output = Self;
 
     fn add(self, rhs: Self) -> Self {
-        Uint128(self.u128() + rhs.u128())
+        Uint128(self.u128().checked_add(rhs.u128()).unwrap())
     }
 }
 
 impl<'a> ops::Add<&'a Uint128> for Uint128 {
     type Output = Self;
 
     fn add(self, rhs: &'a Uint128) -> Self {
-        Uint128(self.u128() + rhs.u128())
+        Uint128(self.u128().checked_add(rhs.u128()).unwrap())
     }
 }
 
 impl ops::AddAssign<Uint128> for Uint128 {
     fn add_assign(&mut self, rhs: Uint128) {
-        self.0 += rhs.u128();
+        self.0 = self.0.checked_add(rhs.u128()).unwrap();
     }
 }
 
 impl<'a> ops::AddAssign<&'a Uint128> for Uint128 {
     fn add_assign(&mut self, rhs: &'a Uint128) {
-        self.0 += rhs.u128();
-    }
-}
-
-impl ops::Sub<Uint128> for Uint128 {
-    type Output = StdResult<Self>;
-
-    fn sub(self, other: Uint128) -> StdResult<Self> {
-        self.sub(&other)
-    }
-}
-
-impl<'a> ops::Sub<&'a Uint128> for Uint128 {
-    type Output = StdResult<Self>;
-
-    fn sub(self, rhs: &'a Uint128) -> StdResult<Self> {
-        let (min, sub) = (self.u128(), rhs.u128());
-        min.checked_sub(sub)
-            .map(Uint128)
-            .ok_or_else(|| StdError::underflow(min, sub))
+        self.0 = self.0.checked_add(rhs.u128()).unwrap();
     }
 }
 
@@ -748,8 +803,7 @@ mod tests {
         assert_eq!(a + &b, Uint128(35801));
 
         // test - with owned and reference right hand side
-        assert_eq!((b - a).unwrap(), Uint128(11111));
-        assert_eq!((b - &a).unwrap(), Uint128(11111));
+        assert_eq!((b.checked_sub(a)).unwrap(), Uint128(11111));
 
         // test += with owned and reference right hand side
         let mut c = Uint128(300000);
@@ -760,15 +814,11 @@ mod tests {
         assert_eq!(d, Uint128(323456));
 
         // error result on underflow (- would produce negative result)
-        let underflow_result = a - b;
-        match underflow_result.unwrap_err() {
-            StdError::Underflow {
-                minuend,
-                subtrahend,
-                ..
-            } => assert_eq!((minuend, subtrahend), (a.to_string(), b.to_string())),
-            err => panic!("Unexpected error: {:?}", err),
-        }
+        let underflow_result = a.checked_sub(b);
+        let OverflowError {
+            operand1, operand2, ..
+        } = underflow_result.unwrap_err();
+        assert_eq!((operand1, operand2), (a.to_string(), b.to_string()));
     }
 
     #[test]
@@ -856,4 +906,54 @@ mod tests {
         let sum_as_owned = nums.into_iter().sum();
         assert_eq!(expected, sum_as_owned);
     }
+
+    #[test]
+    fn uint128_methods() {
+        // checked_*
+        assert!(matches!(
+            Uint128(u128::MAX).checked_add(Uint128(1)),
+            Err(OverflowError { .. })
+        ));
+        assert!(matches!(
+            Uint128(0).checked_sub(Uint128(1)),
+            Err(OverflowError { .. })
+        ));
+        assert!(matches!(
+            Uint128(u128::MAX).checked_mul(Uint128(2)),
+            Err(OverflowError { .. })
+        ));
+        assert!(matches!(
+            Uint128(u128::MAX).checked_div(Uint128(0)),
+            Err(DivideByZeroError { .. })
+        ));
+        assert!(matches!(
+            Uint128(u128::MAX).checked_div_euclid(Uint128(0)),
+            Err(DivideByZeroError { .. })
+        ));
+        assert!(matches!(
+            Uint128(u128::MAX).checked_rem(Uint128(0)),
+            Err(DivideByZeroError { .. })
+        ));
+
+        // saturating_*
+        assert_eq!(
+            Uint128(u128::MAX).saturating_add(Uint128(1)),
+            Uint128(u128::MAX)
+        );
+        assert_eq!(Uint128(0).saturating_sub(Uint128(1)), Uint128(0));
+        assert_eq!(
+            Uint128(u128::MAX).saturating_mul(Uint128(2)),
+            Uint128(u128::MAX)
+        );
+        assert_eq!(Uint128(u128::MAX).saturating_pow(2), Uint128(u128::MAX));
+
+        // wrapping_*
+        assert_eq!(Uint128(u128::MAX).wrapping_add(Uint128(1)), Uint128(0));
+        assert_eq!(Uint128(0).wrapping_sub(Uint128(1)), Uint128(u128::MAX));
+        assert_eq!(
+            Uint128(u128::MAX).wrapping_mul(Uint128(2)),
+            Uint128(u128::MAX - 1)
+        );
+        assert_eq!(Uint128(u128::MAX).wrapping_pow(2), Uint128(1));
+    }
 }
```

### packages/storage/src/singleton.rs
```diff
@@ -131,7 +131,7 @@ mod tests {
     use cosmwasm_std::testing::MockStorage;
     use serde::{Deserialize, Serialize};
 
-    use cosmwasm_std::StdError;
+    use cosmwasm_std::{OverflowError, OverflowOperation, StdError};
 
     #[derive(Serialize, Deserialize, PartialEq, Debug)]
     struct Config {
@@ -251,9 +251,15 @@ mod tests {
         };
         writer.save(&cfg).unwrap();
 
-        let output = writer.update(&|_c| Err(StdError::underflow(4, 7)));
+        let output = writer.update(&|_c| {
+            Err(StdError::from(OverflowError::new(
+                OverflowOperation::Sub,
+                4,
+                7,
+            )))
+        });
         match output.unwrap_err() {
-            StdError::Underflow { .. } => {}
+            StdError::Overflow(_) => {}
             err => panic!("Unexpected error: {:?}", err),
         }
         assert_eq!(writer.load().unwrap(), cfg);
```
