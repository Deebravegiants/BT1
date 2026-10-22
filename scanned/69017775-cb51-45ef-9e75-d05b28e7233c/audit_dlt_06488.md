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
                Stream(_token, _streamId, _total, 0, _start, _cliff, _end);

            // We do not want activePaymentReceivers[client] to have duplicate paymentReceiver entries
            // So we avoid pushing the _paymentReceiver to activePaymentReceivers[client] if it already exists
            if (
                _findAddressInActiveStreams(client, _paymentReceiver)
                    == type(uint).max
            ) {
                activePaymentReceivers[client].push(_paymentReceiver);
            }

            activeStreams[client][_paymentReceiver].push(_streamId);

            emit StreamingPaymentAdded(
                client,
                _paymentReceiver,
                _token,
                _streamId,
                _total,
                _start,
                _cliff,
                _end
            );
        }
    }
```

The contract uses `_findAddressInActriveStreams` to see if the `_paymentReceiver` is already active, if he isn't he is pushed into the array for said `client`.

```sol
function _findAddressInActiveStreams(
        address client,
        address paymentReceiver
    ) internal view returns (uint) {
        address[] memory receiverSearchArray = activePaymentReceivers[client];

        uint length = activePaymentReceivers[client].length;
        for (uint i; i < length;) {
            if (receiverSearchArray[i] == paymentReceiver) {
                return i;
            }
            unchecked {
                ++i;
            }
        }
        return type(uint).max;
    }
```

This introduces a problem, as there is no limit on how large the `activePaymentsReceiver[client]` array can become. This can be weaponized by a malicious user to create a massive array, which has to be looped over each time in order to add new payment receivers.

The most dangerous way to exploit this, would be through `LM_PC_Staking_v1`, as it allows any address to `stake` and then claim rewards, which are transferred through a payment processor, in our case `PP_Streaming_v1`.

Note that the bogus streams cannot be removed through `removePaymentForSpecificStream` as when `LM_PC_Staking_v1` calls `_addPayment`, `end = block.timestamp` and `removePaymentForSpecificStream` requires for the stream to not have ended.

```sol
function removePaymentForSpecificStream(
        address client,
        address paymentReceiver,
        uint streamId
    ) external onlyOrchestratorAdmin {
        // First, we give the streamed funds from this specific streamId to the beneficiary
        _claimForSpecificStream(client, paymentReceiver, streamId);

        // Now, we need to check when this function was called to determine if we need to delete the details pertaining to this stream or not
        // We will delete the payment order in question, if it hasn't already reached the end of its duration.
        if (
            block.timestamp
                < endForSpecificStream(client, paymentReceiver, streamId)
        ) {
            _afterClaimCleanup(client, paymentReceiver, streamId);
        }
    }
```


**Attack Scenario**\
1. A malicious user uses `stake` with 1 wei, with a massive amount of addresses.
2. Rewards accumulate and he then calls `claimRewards` for each of the addresses he staked with.
3. This will fill up `activePaymentReceivers` and they won't be cleared until they are claimed.
4. A real user wants to `claimRewards`, but he can't as `activePaymentReceivers` has become so big that the gas costs exceed the gas block limit, effectively bricking the reward logic for `LM_PC_Staking_v1`.
5. This will also completely brick `stake` and `unstake`, as both functions call `_distributeRewards`, which completely bricks the entire `LM_PC_Staking_v1` contract. Users can't deposit, withdraw or claim their rewards, withdrawing being the most impactful as it freezes user funds.

Note that a fix for this would be changing out the payment processor through the orchestrator, but if `activePaymentReceivers` have any real users that haven't claimed their rewards yet, they won't be able to, when they attempt to claim, `_claimForSpecificStream` will revert when calling `amountPaid` on the `client`, as only the `paymentProcessor` of the orchestrator can call the function.

```sol
 function amountPaid(address token, uint amount) external virtual {
        // Ensure caller is authorized to act as payment processor.
        if (!_isAuthorizedPaymentProcessor(IPaymentProcessor_v1(_msgSender())))
        {
            revert Module__ERC20PaymentClientBase__CallerNotAuthorized();
        }

        // reduce outstanding token amount by the given amount
        _outstandingTokenAmounts[token] -= amount;
    }

 function _isAuthorizedPaymentProcessor(IPaymentProcessor_v1 who)
        internal
        view
        virtual
        returns (bool)
    {
        return __Module_orchestrator.paymentProcessor() == who;
    }
```

This effectively increases the DoS of `LM_PC_Staking_v1` as users have to wait until all real users claimed their rewards and `activePaymentReceivers` only has the malicious addresses in it, after which the orchestrator has to change the payment processor to back to a new one, so that users can `stake, unstake or claimRewards`.

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

Don't keep "pending" users in an array, as it can grow extremely large.
Another workaround would be to introduce an admin function that can be used to target a specific stream by it's id in order to remove it.
