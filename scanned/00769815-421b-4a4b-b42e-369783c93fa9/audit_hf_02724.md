# [M] Use of `payable.transfer

## Summary
Severity: Medium
Contest weight: 0.3175
Dataset id: 14806
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The use of `payable.transfer()` is heavily frowned upon because it can lead to the locking of funds. The `transfer()` call requires that the recipient has a `payable` callback, only provides 2300 gas for its operation. This means the following cases can cause the transfer to fail:

  * The contract does not have a `payable` callback
  * The contract’s `payable` callback spends more than 2300 gas (which is only enough to emit something)
  * The contract is called through a proxy which itself uses up the 2300 gas

If a user falls into one of the above categories, they’ll be unable to receive funds from the vault in a migration wrapper. Inaccessible funds means loss of funds, which is Medium severity.

## Proof of Concept
Both `leave()`:
    
    File: src/modules/Migration.sol   #1
    
    159           uint256 ethAmount = userProposalEth[_proposalId][msg.sender];
    160           proposal.totalEth -= ethAmount;
    161           userProposalEth[_proposalId][msg.sender] = 0;
    162   
    163           // Withdraws fractions from contract back to caller
    164           IFERC1155(token).safeTransferFrom(
    165               address(this),
    166               msg.sender,
    167               id,
    168               amount,
    169               ""
    170           );
    171           // Withdraws ether from contract back to caller
    172           payable(msg.sender).transfer(ethAmount);

and `withdrawContribution()` use `payable.transfer()`
    
    File: src/modules/Migration.sol   #2
    
    320           // Temporarily store user's eth for the transfer
    321           uint256 userEth = userProposalEth[_proposalId][msg.sender];
    322           // Udpates ether balance of caller
    323           userProposalEth[_proposalId][msg.sender] = 0;
    324           // Withdraws ether from contract back to caller
    325           payable(msg.sender).transfer(userEth);

While they both use `msg.sender`, the funds are tied to the address that deposited them (lines 159 and 321), and there is no mechanism to change the owner of the funds to an alternate address.

## Recommendation
Use `address.call{value:x}()` instead.

After an unsuccessful migration, a multisig user (or other contract) may find their funds unrecoverable. Since a contract is able to enter a migration successfully and there is no way to specify an alternative send to address or migrate their escrowed funds to another account — assets can be lost; as the warden points out here. I agree with Medium risk for this.
