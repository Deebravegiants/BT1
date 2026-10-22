# [M] `wrapNativeTokenInWallet` is not compatible with Arbitrum's WETH implementation

## Summary
Severity: Medium
Contest weight: 0.1767
Dataset id: 21667
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`VaultLogic.wrapNativeTokenInWallet()` is used in a number of places. It’s mainly used to store `msg.value` into `WETH` and then transfer it to `msg.sender`.

      function wrapNativeTokenInWallet(address wrappedNativeToken, address user, uint256 amount) internal {
        require(amount > 0, Errors.INVALID_AMOUNT);

        IWETH(wrappedNativeToken).deposit{value: amount}();

        bool success = IWETH(wrappedNativeToken).transferFrom(address(this), user, amount);
        require(success, Errors.TOKEN_TRANSFER_FAILED);
      }

The token transfer is done using the `transferFrom` method. This works fine on most chains (Ethereum, Optimism, Polygon, BSC) which use the standard WETH9 contract that handles the case src == msg.sender:

    WETH9.sol
    if (src != msg.sender && allowance[src][msg.sender] != uint(- 1)) {
                require(allowance[src][msg.sender] >= wad);
                allowance[src][msg.sender] -= wad;
            }

The problem is that the WETH implementation on Arbitrum uses [a different contract](https://arbiscan.io/address/0x8b194beae1d3e0788a1a35173978001acdfba668#code), and does not have this `src == msg.sender` handling.

## Recommendation
function wrapNativeTokenInWallet(address wrappedNativeToken, address user, uint256 amount) internal {
        require(amount > 0, Errors.INVALID_AMOUNT);

        IWETH(wrappedNativeToken).deposit{value: amount}();

        bool success = IWETH(wrappedNativeToken).transfer(user, amount);
        require(success, Errors.TOKEN_TRANSFER_FAILED);
      }
