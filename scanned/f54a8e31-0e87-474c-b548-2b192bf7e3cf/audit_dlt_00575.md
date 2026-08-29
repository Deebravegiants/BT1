# [?] fix: prevent unsigned underflow in eth_feeHistory reward bounds (#10060)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-03-19
Source: https://github.com/besu-eth/besu/commit/09dcb17623cf1fc1346044b3d59719ac47415d44
Type: security-commit

## Details
fix: prevent unsigned underflow in eth_feeHistory reward bounds (#10060)

* fix: prevent unsigned underflow in eth_feeHistory reward bounds

Wei.subtract() wraps around on underflow since Wei is unsigned 256-bit.
In boundRewards(), when nextBaseFee exceeds gasPriceLowerBound (happens
when querying historical blocks from a higher-fee period), the
subtraction produces a near-2^256 value. This corrupts every reward
entry in the response, causing wallets to suggest absurd gas prices.

Floor the priority fee delta at zero when nextBaseFee is larger.

Signed-off-by: Shridhar Panigrahi <sridharpanigrahi2006@gmail.com>

* test: address review feedback on eth_feeHistory underflow fix

  - Shorten verbose comment in boundRewards to a single line
  - Replace indirect <= 2L assertion with exact expected reward values
  - Add equal-case test (nextBaseFee == lowerBoundGasPrice) confirming
    lowerBoundPriorityFee is Wei.ZERO and rewards are correct

Signed-off-by: Shridhar Panigrahi <sridharpanigrahi2006@gmail.com>

---------

Signed-off-by: Shridhar Panigrahi <sridharpanigrahi2006@gmail.com>
Co-authored-by: Sally MacFarlane <macfarla.github@gmail.com>
