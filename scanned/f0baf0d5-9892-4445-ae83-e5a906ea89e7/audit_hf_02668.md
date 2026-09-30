# [M] Potentially Outdated ezETH/ETH Rate On L2 Can Cause Insolvency

## Summary
Severity: Medium
Contest weight: 0.2619
Dataset id: 14451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to delays in ezETH/ETH price oracle updates and sweeping, xezETH on L2s will be undercollateralised by the amount of ezETH locked in the xezETH lockbox on L1. This can lead to insolvency if a large number of xezETH tokens are bridged back to L1.
There are two ways xRenzoBridge can receive the ezETH/ETH mint rate:
1. Via a Connext or Chainlink CCIP message from L1 via xRenzoBridge::sendPrice()
2. Via a custom Chainlink price feed on L2 that reads from BalancerRateProvider::getRate() on L1
Messages sent through Connext and Chainlink CCIP incur a delay as time is needed to ﬁnalise and verify messages. For Connext, the ConnextReceiver requires authenticated calldata as the _originSender is checked, hence the message goes through Connext's slow path which can take upwards of 4 hours to complete. Chainlink CCIP execution latency largely depends on Ethereum's block ﬁnality time, which is approximately 15 minutes.
A custom Chainlink price feed incurs less latency than sending messages via Connext and CCIP, but still unavoidably has minor discrepancies in the ezETH/ETH rate due to the set deviation threshold. The price feed will only update its price if the new price deviates by more than the threshold, which is currently set as 0.5% for Arbitrum’s ezETH/ETH exchange rate feed. This value is too high for ezETH/ETH as the rate slowly appreciates over time as staking rewards are received. Hence, it is likely that the L2 price feed will lag behind the L1 rate.
Furthermore, there is another delay involved with sweeping nextWETH and initiating the Connext xCall. Sweepers are required to pay for Connext's relayer fees upfront, which is covered by depositors based on a ﬂat fee of 0.05%.
Relayer fees are variable and can be considerably higher than the collected bridge fees, hence sweepers may wait for a prolonged period of time for the accrued bridge fees to be enough to cover the relayer fee before sweeping the batched funds.
Due to these delays, the mint rate of xezETH on L2s will lag behind the true mint rate on L1. Since ezETH/ETH is monotonically increasing during normal behaviour, it's extremely likely that the mint rate on L2 at time of the L2 deposit is lower than on the mint rate on L1 at time of the L1 deposit. Users depositing on L2s will receive more xezETH than the amount of ezETH that will be minted and locked once the funds are sweeped and deposited into RestakeManager on L1. This results in an undercollateralisation of xezETH in the xezETHLockbox, which can lead to insolvency of the lockbox if the xezETH is bridged back to L1.

## Recommendation
Similarly to RENZO-10, instead of optimistically minting xezETH based on a potentially outdated price, the use of xCall callbacks and a credit token can prevent insolvency by ensuring that the correct amount of xezETH is minted on L2s.
Restaking Smart Contract Review
However, the use of a credit token negatively impacts user experience. Alternatively, to minimise the Chainlink price feed update delays, the deviation threshold can be reduced. As a reference, a deviation of 0.2% is used for Rocketpool's rETH/ETH exchange rate feeds.
