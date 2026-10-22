# [M] Outdated ERC721 Implementation

## Summary
Severity: Medium
Contest weight: 0.1720
Dataset id: 14216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Dapper Ethereum smart contract wallet (CoreWallet, deployed in its cloned and full versions) inherits the ERC721Receiver contract and as such, implements the onERC721Received() function.
This function in non-compliant with the ERC721 standard as it does not take the right arguments as specified by the standard:
• ERC721 Standard [1]: onERC721Received(address, address, uint256, bytes);
• Dapper implementation (ERC721Receiver): onERC721Received(address, uint256, bytes);
This function is to be called by ERC721 contracts when a safeTransferFrom is made to a contract address. Typically, these contracts would implement a function which veriﬁes that the recipient address, when a contract, is compliant with the ERC721TokenReceiver interface, expecting the onERC721Received() function of the Dapper contract to return 0x150b7a02 (equals to bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"))).
Since the Dapper wallet returns 0xf0b9e5ba (equals to bytes4(keccak256("onERC721Received(address,uint256,bytes)"))), any ERC721 transfer to a Dapper smart contract wallet would eﬀectively fail.
This is illustrated in our test suite, refer to tests/test_erc721.py.

## Recommendation
Change the ERC721Receiver and ERC721Receivable contracts to comply with the ERC721 standard. Speciﬁcally, change the onERC721Received() function to take an additional address (i.e. the address calling the safeTransferFrom()).
