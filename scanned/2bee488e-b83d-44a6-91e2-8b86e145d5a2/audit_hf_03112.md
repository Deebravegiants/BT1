# [M] Use safeTransferFrom() instead of transferFro

## Summary
Severity: Medium
Contest weight: 0.1640
Dataset id: 17574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is recommended to use safeTransferFrom() instead of transferFrom() when transferring ERC721s out of the vault. The transferFrom() method is used instead of safeTransferFrom(), which I assume is a gas-saving measure. I however argue that this isn’t recommended because: OpenZeppelin’s documentation discourages the use of transferFrom(); use safeTransferFrom() whenever possible; The recipient could have logic in the onERC721Received() function, which is only triggered in the safeTransferFrom() function and not in transferFrom(). A notable example of such contracts is the Sudoswap pair: function onERC721Received( address, address, uint256 id, bytes memory ) public virtual returns (bytes4) { IERC721 _nft = nft(); if (msg.sender == address(_nft)) { idSet.add(id); } return this.onERC721Received.selector; } It helps ensure that the recipient is indeed capable of handling ERC721s. While unlikely because the recipient is the function caller, there is the potential loss of NFTs should the recipient is unable to handle the sent ERC721s.

## Recommendation
Use safeTransferFrom() when sending out the NFT from the vault. - IERC721(_erc721Address).transferFrom(address(this), msg.sender, _id); + IERC721(_erc721Address).safeTransferFrom(address(this), msg.sender, _id); is applied to Transfer.sol as well. Added safeTransferFrom in withdraw function. Fix here. Makes sense to be compatible with contracts as recipients. Confirmed fix.
