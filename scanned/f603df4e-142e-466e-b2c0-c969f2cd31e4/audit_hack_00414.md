# [H] Secret Network incident: An attacker exploited a vulnerability in Secret Network’s modified CW20-ICS20 contract used for the Axelar IBC bridge. By creating

## Summary
Severity: High
Target: Secret Network
Loss: $ 4,670,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-10
Source: https://x.com/axelar/status/2068355855565594885
Type: slowmist-incident

## Details
An attacker exploited a vulnerability in Secret Network’s modified CW20-ICS20 contract used for the Axelar IBC bridge. By creating a fake Cosmos chain and sending forged IBC deposit packets (the contract had critical source-channel verification checks commented out), the attacker minted approximately $4.67 million in unbacked “saTokens” (Secret-wrapped versions of Axelar-bridged assets). These were redeemed through the legitimate bridge channel, draining real assets from Axelar’s escrow in about 18 minutes. Funds were then bridged out via Osmosis to Ethereum and mostly cashed out on exchanges. The incident was detected on June 17 and publicly disclosed on June 19. Axelar paused the Secret bridge routes; its core protocol and other chains were unaffected. No funds have been recovered.
