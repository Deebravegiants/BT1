# [C] Remote donations are stuck

## Summary
Severity: Critical
Contest weight: 0.4099
Dataset id: 9437
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users interact with RemoteDonate to perform donations on non-Ethereum chains. And the donation will be withdrawn remotely to the donationReceiver on Ethereum chain via Stargate cross-chain transfer.
Due to the cross-chain transfer, an LZ fee is required to be paid via msg.value while transferring the donationAmount to Ethereum chain.
The issue is that donationAmount is assigned the value of address(this).balance, which actually includes the msg.value meant for the transfer across chain.
That will cause the IOFT(stargate).send{ value: msg.value + donationAmountNative } to fail as it is sending more than address(this).balance.
The impact of this is that withdrawals for remote donations will always fail, causing them to be stuck within the contract.
```solidity
function withdrawDonation(Currency _currency, uint256 _minAmount) external payable {
    address stargate;
    uint256 donationAmount;
    uint256 donationAmountNative;
    if (_currency == Currency.USDC && stargateUsdc != address(0)) {
        stargate = stargateUsdc;
        donationAmount = tokenUsdc.balanceOf(address(this));
    } else if (_currency == Currency.USDT && stargateUsdt != address(0)) {
        stargate = stargateUsdt;
        donationAmount = tokenUsdt.balanceOf(address(this));
    } else if (_currency == Currency.Native && stargateNative != address(0)) {
        stargate = stargateNative;
        // @audit this would have included the LZ fee (msg.value) as well
        donationAmount = address(this).balance;
        donationAmountNative = donationAmount;
    } else {
        revert UnsupportedCurrency(_currency);
    }
    // sends via taxi
    bytes memory emptyBytes = new bytes(0);
    SendParam memory sendParams = SendParam({
        dstEid: remoteEid, // only send to ethereum
        to: bytes32(uint256(uint160(donationReceiver))),
        amountLD: donationAmount,
        minAmountLD: _minAmount,
        extraOptions: emptyBytes,
        composeMsg: emptyBytes,
        oftCmd: emptyBytes // type taxi
    });
    // combine the msg value in addition to the donation amount
    // in non native currencies this will just be 0
    // solhint-disable-next-line check-send-result
    // @audit this will always fail since it is sending more than address(this).balance
    IOFT(stargate).send{ value: msg.value + donationAmountNative }(
        sendParams,
        MessagingFee(msg.value, 0),
        msg.sender // refund any excess native to the sender
    );
    emit DonationWithdrawn(_currency, donationReceiver, donationAmount);
}
```

## Recommendation
Make the following change to calculate the actual donation amount for transfer.
```solidity
} else if (_currency == Currency.Native && stargateNative != address(0)) {
    stargate = stargateNative;
    - donationAmount = address(this).balance;
    + donationAmount = address(this).balance - msg.value;
    donationAmountNative = donationAmount;
} else {
```
