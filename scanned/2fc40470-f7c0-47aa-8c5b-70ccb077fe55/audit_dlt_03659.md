# [M] Early attacker can DOS rToken issuance

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-02-reserve-mitigation-contest
Published: 2023-02-14
Source: https://github.com/code-423n4/2023-02-reserve-mitigation-contest-findings/issues/13
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/27a3472d553b4fa54f896596007765ec91941348/contracts/p1/RToken.sol#L308-L312
https://github.com/reserve-protocol/protocol/blob/27a3472d553b4fa54f896596007765ec91941348/contracts/p1/RToken.sol#L132


# Vulnerability details

## Impact
An early attacker can DOS the `issue` functionality in the `RToken` contract.  

No issuances can be made. And the DOS cannot be recovered from. It is permanent.  

## Proof of Concept
You can add the following test to the `Furnace.test.ts` file and execute it with `yarn hardhat test --grep 'M-05 Mitigation Error: DOS issue'`.  

```typescript
describe('M-05 Mitigation Error', () => {
    beforeEach(async () => {
      // Approvals for issuance
      await token0.connect(addr1).approve(rToken.address, initialBal)
      await token1.connect(addr1).approve(rToken.address, initialBal)
      await token2.connect(addr1).approve(rToken.address, initialBal)
      await token3.connect(addr1).approve(rToken.address, initialBal)

      await token0.connect(addr2).approve(rToken.address, initialBal)
      await token1.connect(addr2).approve(rToken.address, initialBal)
      await token2.connect(addr2).approve(rToken.address, initialBal)
      await token3.connect(addr2).approve(rToken.address, initialBal)

      // Issue tokens
      const issueAmount: BigNumber = bn('100e18')
      // await rToken.connect(addr1).issue(issueAmount)
      // await rToken.connect(addr2).issue(issueAmount)
    })

    it('M-05 Mitigation Error: DOS issue', async () => {
      /* attack vector actually so bad that attacker can block issuance a loooong time?
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-02-reserve-mitigation-contest-findings/issues/13_
