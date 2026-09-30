# [H] backdoor in `withdrawRedundant`

## Summary
Severity: High
Contest weight: 0.7513
Dataset id: 1426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `Vault.withdrawRedundant` has wrong logic that allows the admins to steal the underlying vault token.
    
```solidity
function withdrawRedundant(address _token, address _to)
    external
    override
    onlyOwner
{
    if (
        _token == address(token) &&
        balance < IERC20(token).balanceOf(address(this))
    ) {
        uint256 _redundant = IERC20(token).balanceOf(address(this)) -
            balance;
        IERC20(token).safeTransfer(_to, _redundant);
    } else if (IERC20(_token).balanceOf(address(this)) > 0) {
        // @audit they can rug users. let's say balance == IERC20(token).balanceOf(address(this)) => first if false => transfers out everything
        IERC20(_token).safeTransfer(
            _to,
            IERC20(_token).balanceOf(address(this))
        );
    }
}
```

## Recommendation
I think the devs wanted this logic from the code instead:
    
```solidity
function withdrawRedundant(address _token, address _to)
    external
    override
    onlyOwner
{
    if (
        _token == address(token)
    ) {
        if (balance < IERC20(token).balanceOf(address(this))) {
            uint256 _redundant = IERC20(token).balanceOf(address(this)) -
                balance;
            IERC20(token).safeTransfer(_to, _redundant);
        }
    } else if (IERC20(_token).balanceOf(address(this)) > 0) {
        IERC20(_token).safeTransfer(
            _to,
            IERC20(_token).balanceOf(address(this))
        );
    }
}
```
similar to PVE03 (Peckshield audit) We will create a PR and merge after we merge both audit/code4rena and audit/peckshield branches in the InsureDAO repository.
