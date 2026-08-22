# [M] PP_Streaming_v1.sol#_findAddressInActiveStreams() - `activePaymentReceivers` can become so large that it's impossible to process more payments, effectively bricking the processor

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-09
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/85
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @EgisSec
**Submission hash (on-chain):** 0x207a511e3877676901a37fb4cf795d103127f27981a70b05da96ce470b43a0a6
**Severity:** medium

**Description:**
**Description**\
`PP_Streaming_v1` is one of the two payment processors that the protocol implements.

It utilizes streams, paying out the funds over a period of time, instead of all at once compared to `PP_Simple_v1`.

Because of this, users have to claim their streams instead of being payed outright.

The contract utilizes the `activePaymentReceivers` mapping to keep track which `client` has `paymentReceivers` (recipients).

They are added when `_addPayment` is called.

```sol
function _addPayment(
        address client,
        address _paymentReceiver,
        address _token,
        uint _streamId,
        uint _total,
        uint _start,
        uint _cliff,
        uint _end
    ) internal {
        ++numStreams[client][_paymentReceiver];
        if (
            !validPaymentReceiver(_paymentReceiver) || !validTotal(_total)
                || !validTimes(_start, _cliff, _end) || !validPaymentToken(_token)
        ) {
            emit InvalidStreamingOrderDiscarded(
                _paymentReceiver, _token, _total, _start, _cliff, _end
            );
        } else {
            streams[client][_paymentReceiver][_streamId] =
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/85_
