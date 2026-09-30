# [?] evm: use 10% of not used gas to prevent gas power exhaustion attacks

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-12-26
Source: https://github.com/0xsoniclabs/sonic/commit/5608dc4c82d6fdf831d87e7020a1d14c5bd68e54
Type: security-commit

## Details
evm: use 10% of not used gas to prevent gas power exhaustion attacks

## Patch
### evmcore/state_transition.go
```diff
@@ -213,6 +213,10 @@ func (st *StateTransition) TransitionDb() (ret []byte, usedGas uint64, fee *big.
 		st.state.SetNonce(msg.From(), st.state.GetNonce(sender.Address())+1)
 		ret, st.gas, vmerr = evm.Call(sender, st.to(), st.data, st.gas, st.value)
 	}
+	// use 10% of not used gas
+	if err = st.useGas(st.gas / 10); err != nil {
+		return nil, 0, common.Big0, false, err
+	}
 	if vmerr != nil {
 		log.Debug("VM returned with error", "err", vmerr)
 		// The only possible consensus-error would be if there wasn't
```
