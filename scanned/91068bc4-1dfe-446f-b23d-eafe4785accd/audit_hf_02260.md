# [M] Revised Handling of SendFrom Message in liquidity_token

## Summary
Severity: Medium
Contest weight: 0.2461
Dataset id: 12400
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Levana protocol has a core liquidity contract which enforces the logic to ensure the execution must come from the liquidity_tokens proxy contract. With that, the function market_execute_liquidity_token() makes a special handling of the LiquidityTokenExecuteMsg::Send message. The goal here is the messages to the destination contract come from the proxy rather than the market. While reviewing their logic, we notice that the current handling may be expanded to cover another LiquidityTokenExecuteMsg::SendFrom message.
Public
In the following, we show the related market_execute_liquidity_token() function that handles the LiquidityTokenExecuteMsg::Send message. However, it comes to our attention that the similar handling should be applied to another message LiquidityTokenExecuteMsg::SendFrom. Otherwise, the SendFrom message may be sent from the market contract, not the proxy.
```rust
pub(crate) fn market_execute_liquidity_token(
    &self,
    ctx: &mut StateContext,
    sender: Addr,
    msg: LiquidityTokenExecuteMsg,
) -> Result<()> {
    let (msg, send) = match msg {
        // Send needs special handling to ensure the messages to the destination contract come from the proxy, not the market.
        LiquidityTokenExecuteMsg::Send {
            contract,
            amount,
            msg,
        } => {
            let send = ReceiverExecuteMsg::Receive(Cw20ReceiveMsg {
                sender: sender.clone().into(),
                amount,
                msg,
            });
            let msg = LiquidityTokenExecuteMsg::Transfer {
                recipient: contract.clone(),
                amount,
            };
            (msg, Some((contract, send)))
        }
        msg => (msg, None),
    };
    ctx.response.add_execute_submessage_oneshot(
        self.market_addr(ctx.storage)?,
        &MarketExecuteMsg::LiquidityTokenProxy {
            sender: sender.into(),
            kind: get_kind(ctx.storage)?,
            msg,
        },
    );
    // We need to sequence this submessage after the previous one to ensure the receiving contract has the expected balance.
    if let Some((contract, send)) = send {
        ctx.response.add_execute_submessage_oneshot(contract, &send)?;
    }
    Ok(())
```
Public

## Recommendation
Revise the above routine to similarly handle the LiquidityTokenExecuteMsg::SendFrom message.
