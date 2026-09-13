# [M] Out of gas with the nested loop across all plugins

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L346-L379
Type: audit-issue

## Details
# Out of gas with the nested loop across all plugins

## Summary

DOS becomes quite probable with the growth of the number of plugins as double loop over all the plugins array is performed on core operations.

## Vulnerability Detail

Along with the growth of the number of plugins the gas usage will grow at the `n^2` rate as the number of plugin interaction functions run across all the plugins supplying the data to be processed to each of them.

Data is processed with another loop, searching for the right entry linearly each time from the start.

## Impact

If plugin loop runs out of gas, say reaching block gas limit at the extreme, the core fund management functions become unavailable, which means freeze of funds for the all protocol users.

If a funds bearing plugin to be removed to remedy that, the funds be temporary frozen there.

## Code Snippet

_claimAndExit() runs over plugins via _claim(), then via _notifyStakeChangeAllPlugins():

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L346-L379

```solidity
    /// @notice Claims yield and withdraws some of stake. Everything leftover remains staked
    /// @param account account
    /// @param amount amount to withdraw
    /// @param to account to send withdrawn funds to
    /// @dev The yield of the account is claimed to this contract
    /// @dev Call `notifyStakeChange` on all plugins
    /// @dev Update _stakes[account]
    /// @dev Update _totalStaked
    /// @dev Transfer `amount` of tokens to `to`
    /// @dev Emit StakeChanged
    function _claimAndExit(address account, uint256 amount, address to, bytes calldata auxData) private {
        require(amount <= balanceOf(account, auxData), "Account has insufficient balance");

        // keep track of initial stake
        uint256 oldStake = _stakes[account].latest();
        // xClaimed = total amount claimed
        uint256 xClaimed = _claim(account, address(this), auxData);

        uint256 newStake = oldStake + xClaimed - amount;

        // notify all plugins that account's stake has changed (if the plugin requires)
        _notifyStakeChangeAllPlugins(account, oldStake, newStake);

        // update _stakes
        _stakes[account].push(newStake);

        // decrement _totalStaked
        _totalStaked = _totalStaked - oldStake + newStake;

        // transfer the tokens to `to`
        IERC20Upgradeable(tel).safeTransfer(to, amount);

        emit StakeChanged(account, oldStake, newStake);
    }
```

_claim() calls claim() with the same `auxData` for each plugin:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L262-L281

```solidity
    function _claim(address account, address to, bytes calldata auxData) private returns (uint256) {
        // balance of `to` before claiming
        uint256 balBefore = IERC20Upgradeable(tel).balanceOf(to);

        // call claim on all plugins and count the total amount claimed
        uint256 total;
        for (uint256 i = 0; i < nPlugins; i++) {
            total += IPlugin(plugins[i]).claim(account, to, auxData);
        }

        // make sure `total` actually matches how much we've claimed
        require(IERC20Upgradeable(tel).balanceOf(to) - balBefore == total, "one or more plugins did not send appropriate token amount");

        // only emit Claimed if anything was actually claimed
        if (total > 0) {
            emit Claimed(account, total);
        }

        return total;
    }
```

Each time `auxData` is processed with the cycle that also grows linearly with the number of plugins (all plugin data is there and the one for a particular plugin to be found, starting at the first item each time):

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/libraries/AuxDataLib.sol#L42-L62

```solidity
    /// @dev Parse `data` and return the data that is relevant to `addr`
    function selectRelevantBytes(bytes calldata data, address addr) internal pure returns (bytes memory) {
        // if data is empty, do nothing and return empty bytes
        if (data.length == 0) {
            return "";
        }

        // parse the data into its header and payload
        (HeaderItem[] memory header, bytes memory payload) = parse(data);

        // iterate over HeaderItems until we find the one that matches addr
        for (uint256 i = 0; i < header.length; i++) {
            if (header[i].addr == addr) {
                // once we have found the correct HeaderItem we slice the payload and return
                return payload.slice(header[i].start, header[i].len);
            }
        }

        // if we never found a HeaderItem corresponding to addr, we return empty bytes
        return "";
    }
```

## Tool used

Manual Review

## Recommendation

Consider refactoring the `auxData` usage, so the search over it to happen only once, with only relevant piece to be sent over to the plugin. I.e. consider moving data parsing to StakingModule, where the search for the relevant piece can be done sequentially, remembering the current position.

Also, consider limiting the number of interactions with the full plugin array, for example filtering out the plugins that hold no funds of a particular user. I.e. if there are no funds, no need to notify the stake change.
