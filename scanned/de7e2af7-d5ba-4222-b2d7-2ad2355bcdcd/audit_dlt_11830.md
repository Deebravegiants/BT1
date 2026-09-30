# [?] fix: issue where compiler panics were not detected using Eth-Tester provider (#2187)

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/ape
Published: 2024-07-25
Source: https://github.com/ApeWorX/ape/commit/bcfadd3e6ef99eab717df873c6a0fd0700a0809d
Type: security-commit

## Details
fix: issue where compiler panics were not detected using Eth-Tester provider (#2187)

## Patch
### src/ape/managers/compilers.py
```diff
@@ -300,7 +300,7 @@ def get_custom_error(self, err: ContractLogicError) -> Optional[CustomError]:
               as a custom error.
 
         Returns:
-
+            Optional[:class:`~ape.exceptions.CustomError`]
         """
         message = err.revert_message
         if not message.startswith("0x"):
```

### src/ape_ethereum/ecosystem.py
```diff
@@ -31,6 +31,7 @@
     ConversionError,
     CustomError,
     DecodingError,
+    ProviderError,
     SignatureError,
 )
 from ape.logging import logger
@@ -1417,7 +1418,6 @@ def decode_custom_error(
 
         selector = data[:4]
         input_data = data[4:]
-
         if selector in contract.contract_type.errors:
             abi = contract.contract_type.errors[selector]
             error_cls = contract.get_error_by_signature(abi.signature)
@@ -1439,8 +1439,16 @@ def decode_custom_error(
         except SignatureError:
             return None
 
-        trace = kwargs.get("trace") or self.provider.get_transaction_trace(tx_hash)
-        if not (last_addr := next(trace.get_addresses_used(reverse=True), None)):
+        try:
+            trace = kwargs.get("trace") or self.provider.get_transaction_trace(tx_hash)
+        except NotImplementedError:
+            return None
+
+        try:
+            if not (last_addr := next(trace.get_addresses_used(reverse=True), None)):
+                return None
+        except ProviderError:
+            # When unable to get trace-frames properly, such as eth-tester.
             return None
 
         if last_addr == address:
```

### src/ape_test/provider.py
```diff
@@ -13,7 +13,7 @@
 from eth_utils.exceptions import ValidationError
 from eth_utils.toolz import merge
 from web3 import EthereumTesterProvider, Web3
-from web3.exceptions import ContractPanicError
+from web3.exceptions import ContractLogicError as Web3ContractLogicError
 from web3.providers.eth_tester.defaults import API_ENDPOINTS, static_return
 from web3.types import TxParams
 
@@ -123,7 +123,7 @@ def estimate_gas_cost(
 
         try:
             return estimate_gas(txn_data, block_identifier=block_id)
-        except (ValidationError, TransactionFailed) as err:
+        except (ValidationError, TransactionFailed, Web3ContractLogicError) as err:
             ape_err = self.get_virtual_machine_error(err, txn=txn)
             gas_match = self._INVALID_NONCE_PATTERN.match(str(ape_err))
             if gas_match:
@@ -215,7 +215,7 @@ def send_call(
             else:
                 result = HexBytes("0x")
 
-        except (TransactionFailed, ContractPanicError) as err:
+        except (TransactionFailed, Web3ContractLogicError) as err:
             vm_err = self.get_virtual_machine_error(err, txn=txn)
             if raise_on_revert:
                 raise vm_err from err
@@ -232,7 +232,7 @@ def send_transaction(self, txn: TransactionAPI) -> ReceiptAPI:
         vm_err = None
         try:
             txn_hash = self.web3.eth.send_raw_transaction(txn.serialize_transaction()).hex()
-        except (ValidationError, TransactionFailed) as err:
+        except (ValidationError, TransactionFailed, Web3ContractLogicError) as err:
             vm_err = self.get_virtual_machine_error(err, txn=txn)
             if txn.raise_on_revert:
                 raise vm_err from err
@@ -260,7 +260,7 @@ def send_transaction(self, txn: TransactionAPI) -> ReceiptAPI:
             # Replay txn to get revert reason
             try:
                 self.web3.eth.call(txn_params)
-            except (ValidationError, TransactionFailed) as err:
+            except (ValidationError, TransactionFailed, Web3ContractLogicError) as err:
                 vm_err = self.get_virtual_machine_error(err, txn=receipt)
                 receipt.error = vm_err
                 if txn.raise_on_revert:
@@ -348,7 +348,7 @@ def get_virtual_machine_error(self, exception: Exception, **kwargs) -> VirtualMa
             else:
                 return VirtualMachineError(base_err=exception, **kwargs)
 
-        elif isinstance(exception, ContractPanicError):
+        elif isinstance(exception, Web3ContractLogicError):
             # If the ape-solidity plugin is installed, we are able to enrich the data.
             message = exception.message
             raw_data = exception.data if isinstance(exception.data, str) else "0x"
```

### tests/functional/test_contract_instance.py
```diff
@@ -202,6 +202,15 @@ def test_revert_allow(not_owner, contract_instance):
     contract_instance.setNumber.call(5, raise_on_revert=False)
 
 
+def test_revert_handles_compiler_panic(owner, contract_instance):
+    # note: setBalance is a weird name - it actually adjust the balance.
+    # first, set it to be 1 less than an overflow.
+    contract_instance.setBalance(owner, 2**256 - 1, sender=owner)
+    # then, add 1 more, so it should no overflow and cause a compiler panic.
+    with pytest.raises(ContractLogicError):
+        contract_instance.setBalance(owner, 1, sender=owner)
+
+
 def test_call_using_block_id(vyper_contract_instance, owner, chain, networks_connected_to_tester):
     contract = vyper_contract_instance
     contract.setNumber(1, sender=owner)
```
