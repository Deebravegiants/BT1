# [M] Possible Reentrency not-involving-eth Issues [RCOrderbook.sol]

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-15
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/47
Type: code-finding

## Details
# Handle

maplesyrup


# Vulnerability details

## Impact

2 - Medium Risk
   - Possible reentrancy found in the contract, possible loss of funds due to code manipulation

## Proof of Concept

According to the Slither-analyzer documentation (https://github.com/crytic/slither/wiki/Detector-Documentation#configuration-32): Detection of reentrancy was found in the following functions as there are external calls made before state variables are changed. This can lead to a possible attack on the functions and contract.

Reentrancy found in:

contracts/RCOrderbook.sol

line(s) 280-340

RCOrderbook._newBidInOrderbook(address, address, uint256, uint256, uint256, RCOrderbook.Bid) 

External calls:

	treasury.increaseBidRate(_user,_price) 
	(contracts/RCOrderbook.sol line(s)#328)
	
	transferCard(_market,_card,_oldOwner,_user,_price) 
	(contracts/RCOrderbook.sol line(s)#331)
	
	_rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) 
	(contracts/RCOrderbook.sol line(s)#870)


State variables written after the call(s):

	transferCard(_market,_card,_oldOwner,_user,_price) 
	(contracts/RCOrderbook.sol line(s)#331)
	
	ownerOf[_market][_card] = _newOwner 
	(contracts/RCOrderbook.so line(s)#866)

 -------------------------------------------------------------------

RCOrderbook._removeBidFromOrderbookIgnoreOwner(address,uint256) 
(contracts/RCOrderbook.sol line(s)#492-527):

External calls:

	treasury.decreaseBidRate(_user,_currUser.price) 
	(contracts/RCOrderbook.sol line(s)#499)

State variables written after the call(s):

	index[_user][_market][_card] = 0 
	(contracts/RCOrderbook.sol line(s)#520)
	
	index[_user][user[_user][_index].market][user[_user][_index].token] = _index 
	(contracts/RCOrderbook.sol line(s)#522-524)
	
	user[_tempNext][index[_tempNext][_market][_card]].prev = _tempPrev 
	(contracts/RCOrderbook.sol line(s)#504)
	
	user[_tempPrev][index[_tempPrev][_market][_card]].next = _tempNext 
	(contracts/RCOrderbook.sol line(s)#505)
	
	user[_user][_index] = user[_user][_lastRecord] 
	(contracts/RCOrderbook.sol line(s)#515)
	
	user[_user].pop() 
	(contracts/RCOrderbook.sol line(s)#517)

 -------------------------------------------------------------------

RCOrderbook.closeMarket() 
(contracts/RCOrderbook.sol line(s)#633-669):

External calls:
	treasury.updateRentalRate(_owner,_market,_price,0,block.timestamp) 
	(contracts/RCOrderbook.sol line(s)#641-647)

State variables written after the call(s):
	user[_market][index[_market][_market][i]].prev = _market 
	(contracts/RCOrderbook.sol line(s)#654) 
	
	user[_market][index[_market][_market][i]].next = _market 
	(contracts/RCOrderbook.sol line(s)#655) 
	
	user[_firstBid][index[_market][_firstBid][i]].prev = address(this) 
	(contracts/RCOrderbook.sol line(s)#656)
	
	user[_lastBid][index[_market][_lastBid][i]].next = address(this)
	(contracts/RCOrderbook.sol line(s)#657) 
	
	user[address(this)].push(_newBid) 
	(contracts/RCOrderbook.sol line(s)#667)

 -------------------------------------------------------------------

RCOrderbook.removeBidFromOrderbook(address,uint256) 

(contracts/RCOrderbook.sol line(s)#442-489):

External calls:

	treasury.decreaseBidRate(_user,_currUser.price) 
	(contracts/RCOrderbook.sol line(s)#450)
	
	transferCard(_market,_card,_user,_currUser.next,_price) 
	(contracts/RCOrderbook.sol line(s)#456)
	
	_rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit)
	(contracts/RCOrderbook.sol line(s)#870)
	
	treasury.updateRentalRate(_user,_currUser.next,_currUser.price,_price,block.timestamp) 
	(contracts/RCOrderbook.sol line(s)#457-463)

State variables written after the call(s):

	index[_user][_market][_card] = 0 
	(contracts/RCOrderbook.sol line(s)#482)
	
	index[_user][user[_user][_index].market][user[_user][_index].token] = _index 
	(contracts/RCOrderbook.sol line(s)#484-486)
	
	user[_tempNext][index[_tempNext][_market][_card]].prev = _tempPrev 
	(contracts/RCOrderbook.sol line(s)#468)
	
	user[_tempPrev][index[_tempPrev][_market][_card]].next = _tempNext
	(contracts/RCOrderbook.sol line(s)#469)
	
	user[_user][_index] = user[_user][_lastRecord] 
	(contracts/RCOrderbook.sol line(s)#477) 
	
	user[_user].pop() 
	(contracts/RCOrderbook.sol line(s)#479)

 -------------------------------------------------------------------

RCOrderbook.removeOldBids(address)

(contracts/RCOrderbook.sol line(s)#674-713):

External calls:

	treasury.decreaseBidRate(_user,_price) 
	(contracts/RCOrderbook.sol line(s)#690)


State variables written after the call(s):

	index[_user][_market][i] = 0 
	(contracts/RCOrderbook.sol line(s)#705)
	
	user[_tempNext][index[_tempNext][_market][i]].prev = _tempPrev
	(contracts/RCOrderbook.sol line(s)#698-699)
	
	user[_tempPrev][index[_tempPrev][_market][i]].next = _tempNext 
	(contracts/RCOrderbook.sol line(s)#700-701)
	
	user[_user].pop() 
	(contracts/RCOrderbook.sol line(s)#704)

 -------------------------------------------------------------------

RCOrderbook.removeUserFromOrderbook(address) 

(contracts/RCOrderbook.sol line(s)#575-629):

External calls: 

	treasury.updateRentalRate(_user,_tempNext,user[_user][i].price,_price, block.timestamp) 
	(contracts/RCOrderbook.sol  line(s)#601-607) 
	
	transferCard(_market,_card,_user,_tempNext,_price) 
	(contracts/RCOrderbook.sol line(s)#608)
	
	_rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) 
	(contracts/RCOrderbook.sol line(s)#870)
	
	treasury.decreaseBidRate(_user,user[_user][i].price) 
	(contracts/RCOrderbook.sol line(s)#611)

State variables written after the call(s):

	user[_tempNext][index[_tempNext][user[_user][i].market][user[_user][i].token]].prev = _tempPrev 
	(contracts/RCOrderbook.sol  line(s)#613-616)
	
	user[_tempPrev][index[_tempPrev][user[_user][i].market][user[_user][i].token]].next = _tempNext 
	(contracts/RCOrderbook.sol line(s)#617-620)
	
	user[_user].pop() 
	(contracts/RCOrderbook.sol line(s)#621)

------------------------------------------

As the document mentions, the best way to solve the issue(s) found on reentrancy is to apply the Checks-Effects-Interactions pattern to the following functions.

------------------------------------------

Console output(Slither log):

INFO:Detectors:
Reentrancy in RCMarket._collectRentAction(uint256) (contracts/RCMarket.sol#854-1034):
	External calls:
	- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
	- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
	- _processRentCollection(_user,_card,_timeOfThisCollection) (contracts/RCMarket.sol#1022)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
	State variables written after the call(s):
	- _processRentCollection(_user,_card,_timeOfThisCollection) (contracts/RCMarket.sol#1022)
		- cardTimeLimit[_card] -= _timeHeldToIncrement (contracts/RCMarket.sol#1067)
	- _processRentCollection(_user,_card,_timeOfThisCollection) (contracts/RCMarket.sol#1022)
		- timeLastCollected[_card] = _timeOfCollection (contracts/RCMarket.sol#1075)
Reentrancy in RCOrderbook._newBidInOrderbook(address,address,uint256,uint256,uint256,RCOrderbook.Bid) (contracts/RCOrderbook.sol#280-340):
	External calls:
	- treasury.increaseBidRate(_user,_price) (contracts/RCOrderbook.sol#328)
	- transferCard(_market,_card,_oldOwner,_user,_price) (contracts/RCOrderbook.sol#331)
		- _rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) (contracts/RCOrderbook.sol#870)
	State variables written after the call(s):
	- transferCard(_market,_card,_oldOwner,_user,_price) (contracts/RCOrderbook.sol#331)
		- ownerOf[_market][_card] = _newOwner (contracts/RCOrderbook.sol#866)
Reentrancy in RCMarket._processRentCollection(address,uint256,uint256) (contracts/RCMarket.sol#1052-1083):
	External calls:
	- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
	- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
	State variables written after the call(s):
	- cardTimeLimit[_card] -= _timeHeldToIncrement (contracts/RCMarket.sol#1067)
	- timeLastCollected[_card] = _timeOfCollection (contracts/RCMarket.sol#1075)
Reentrancy in RCOrderbook._removeBidFromOrderbookIgnoreOwner(address,uint256) (contracts/RCOrderbook.sol#492-527):
	External calls:
	- treasury.decreaseBidRate(_user,_currUser.price) (contracts/RCOrderbook.sol#499)
	State variables written after the call(s):
	- index[_user][_market][_card] = 0 (contracts/RCOrderbook.sol#520)
	- index[_user][user[_user][_index].market][user[_user][_index].token] = _index (contracts/RCOrderbook.sol#522-524)
	- user[_tempNext][index[_tempNext][_market][_card]].prev = _tempPrev (contracts/RCOrderbook.sol#504)
	- user[_tempPrev][index[_tempPrev][_market][_card]].next = _tempNext (contracts/RCOrderbook.sol#505)
	- user[_user][_index] = user[_user][_lastRecord] (contracts/RCOrderbook.sol#515)
	- user[_user].pop() (contracts/RCOrderbook.sol#517)
Reentrancy in RCMarket.circuitBreaker() (contracts/RCMarket.sol#1107-1115):
	External calls:
	- orderbook.closeMarket() (contracts/RCMarket.sol#1113)
	State variables written after the call(s):
	- state = States.WITHDRAW (contracts/RCMarket.sol#1114)
Reentrancy in RCOrderbook.closeMarket() (contracts/RCOrderbook.sol#633-669):
	External calls:
	- treasury.updateRentalRate(_owner,_market,_price,0,block.timestamp) (contracts/RCOrderbook.sol#641-647)
	State variables written after the call(s):
	- user[_market][index[_market][_market][i]].prev = _market (contracts/RCOrderbook.sol#654)
	- user[_market][index[_market][_market][i]].next = _market (contracts/RCOrderbook.sol#655)
	- user[_firstBid][index[_market][_firstBid][i]].prev = address(this) (contracts/RCOrderbook.sol#656)
	- user[_lastBid][index[_market][_lastBid][i]].next = address(this) (contracts/RCOrderbook.sol#657)
	- user[address(this)].push(_newBid) (contracts/RCOrderbook.sol#667)
Reentrancy in RCFactory.createMarket(uint32,string,uint32[],string[],address,address,address[],string,uint256) (contracts/RCFactory.sol#465-613):
	External calls:
	- treasury.addMarket(_newAddress) (contracts/RCFactory.sol#569)
	- nfthub.addMarket(_newAddress) (contracts/RCFactory.sol#570)
	- orderbook.addMarket(_newAddress,_tokenURIs.length,minimumPriceIncreasePercent) (contracts/RCFactory.sol#571-575)
	- IRCMarket(_newAddress).initialize(_mode,_timestamps,_tokenURIs.length,totalNftMintCount,_artistAddress,_affiliateAddress,_cardAffiliateAddresses,_creator,_realitioQuestion) (contracts/RCFactory.sol#582-592)
	State variables written after the call(s):
	- totalNftMintCount = totalNftMintCount + _tokenURIs.length (contracts/RCFactory.sol#605)
Reentrancy in RCTreasury.deposit(uint256,address) (contracts/RCTreasury.sol#279-316):
	External calls:
	- erc20.transferFrom(msgSender(),address(this),_amount) (contracts/RCTreasury.sol#298)
	- orderbook.removeOldBids(_user) (contracts/RCTreasury.sol#301)
	State variables written after the call(s):
	- totalDeposits += _amount (contracts/RCTreasury.sol#304)
Reentrancy in RCMarket.lockMarket() (contracts/RCMarket.sol#441-460):
	External calls:
	- collectRentAllCards() (contracts/RCMarket.sol#449)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
		- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
		- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
		- orderbook.findNewOwner(_card,_timeOfThisCollection) (contracts/RCMarket.sol#1025)
	- orderbook.closeMarket() (contracts/RCMarket.sol#450)
	State variables written after the call(s):
	- _incrementState() (contracts/RCMarket.sol#451)
		- state = IRCMarket.States(uint256(state) + (1)) (contracts/RCMarket.sol#1096)
Reentrancy in RCMarket.newRental(uint256,uint256,address,uint256) (contracts/RCMarket.sol#666-734):
	External calls:
	- _userStillForeclosed = orderbook.removeUserFromOrderbook(_user) (contracts/RCMarket.sol#689)
	- orderbook.removeOldBids(_user) (contracts/RCMarket.sol#705)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
		- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
		- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
		- orderbook.findNewOwner(_card,_timeOfThisCollection) (contracts/RCMarket.sol#1025)
	- autoLock() (contracts/RCMarket.sol#671)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- assert(bool)(nfthub.transferNft(_from,_to,_tokenId)) (contracts/RCMarket.sol#367)
		- orderbook.closeMarket() (contracts/RCMarket.sol#450)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
		- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
		- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
		- orderbook.findNewOwner(_card,_timeOfThisCollection) (contracts/RCMarket.sol#1025)
	State variables written after the call(s):
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- cardTimeLimit[_card] -= _timeHeldToIncrement (contracts/RCMarket.sol#1067)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- longestOwner[_card] = _user (contracts/RCMarket.sol#1080)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- longestTimeHeld[_card] = timeHeld[_card][_user] (contracts/RCMarket.sol#1079)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- rentCollectedPerCard[_card] += _rentOwed (contracts/RCMarket.sol#1072)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- rentCollectedPerUser[_user] += _rentOwed (contracts/RCMarket.sol#1071)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- rentCollectedPerUserPerCard[_user][_card] += _rentOwed (contracts/RCMarket.sol#1073)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- timeHeld[_card][_user] += _timeHeldToIncrement (contracts/RCMarket.sol#1069)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- timeLastCollected[_card] = _timeOfCollection (contracts/RCMarket.sol#1075)
		- timeLastCollected[_card] = _timeOfThisCollection (contracts/RCMarket.sol#1031)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- totalRentCollected += _rentOwed (contracts/RCMarket.sol#1074)
	- _collectRent(_card) (contracts/RCMarket.sol#707)
		- totalTimeHeld[_card] += _timeHeldToIncrement (contracts/RCMarket.sol#1070)
Reentrancy in RCOrderbook.removeBidFromOrderbook(address,uint256) (contracts/RCOrderbook.sol#442-489):
	External calls:
	- treasury.decreaseBidRate(_user,_currUser.price) (contracts/RCOrderbook.sol#450)
	- transferCard(_market,_card,_user,_currUser.next,_price) (contracts/RCOrderbook.sol#456)
		- _rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) (contracts/RCOrderbook.sol#870)
	- treasury.updateRentalRate(_user,_currUser.next,_currUser.price,_price,block.timestamp) (contracts/RCOrderbook.sol#457-463)
	State variables written after the call(s):
	- index[_user][_market][_card] = 0 (contracts/RCOrderbook.sol#482)
	- index[_user][user[_user][_index].market][user[_user][_index].token] = _index (contracts/RCOrderbook.sol#484-486)
	- user[_tempNext][index[_tempNext][_market][_card]].prev = _tempPrev (contracts/RCOrderbook.sol#468)
	- user[_tempPrev][index[_tempPrev][_market][_card]].next = _tempNext (contracts/RCOrderbook.sol#469)
	- user[_user][_index] = user[_user][_lastRecord] (contracts/RCOrderbook.sol#477)
	- user[_user].pop() (contracts/RCOrderbook.sol#479)
Reentrancy in RCOrderbook.removeOldBids(address) (contracts/RCOrderbook.sol#674-713):
	External calls:
	- treasury.decreaseBidRate(_user,_price) (contracts/RCOrderbook.sol#690)
	State variables written after the call(s):
	- index[_user][_market][i] = 0 (contracts/RCOrderbook.sol#705)
	- user[_tempNext][index[_tempNext][_market][i]].prev = _tempPrev (contracts/RCOrderbook.sol#698-699)
	- user[_tempPrev][index[_tempPrev][_market][i]].next = _tempNext (contracts/RCOrderbook.sol#700-701)
	- user[_user].pop() (contracts/RCOrderbook.sol#704)
Reentrancy in RCOrderbook.removeUserFromOrderbook(address) (contracts/RCOrderbook.sol#575-629):
	External calls:
	- treasury.updateRentalRate(_user,_tempNext,user[_user][i].price,_price,block.timestamp) (contracts/RCOrderbook.sol#601-607)
	- transferCard(_market,_card,_user,_tempNext,_price) (contracts/RCOrderbook.sol#608)
		- _rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) (contracts/RCOrderbook.sol#870)
	- treasury.decreaseBidRate(_user,user[_user][i].price) (contracts/RCOrderbook.sol#611)
	State variables written after the call(s):
	- user[_tempNext][index[_tempNext][user[_user][i].market][user[_user][i].token]].prev = _tempPrev (contracts/RCOrderbook.sol#613-616)
	- user[_tempPrev][index[_tempPrev][user[_user][i].market][user[_user][i].token]].next = _tempNext (contracts/RCOrderbook.sol#617-620)
	- user[_user].pop() (contracts/RCOrderbook.sol#621)
Reentrancy in RCMarket.setWinner(uint256) (contracts/RCMarket.sol#464-476):
	External calls:
	- lockMarket() (contracts/RCMarket.sol#468)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- assert(bool)(nfthub.transferNft(_from,_to,_tokenId)) (contracts/RCMarket.sol#367)
		- orderbook.closeMarket() (contracts/RCMarket.sol#450)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
		- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
		- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
		- orderbook.findNewOwner(_card,_timeOfThisCollection) (contracts/RCMarket.sol#1025)
	State variables written after the call(s):
	- _incrementState() (contracts/RCMarket.sol#473)
		- state = IRCMarket.States(uint256(state) + (1)) (contracts/RCMarket.sol#1096)
Reentrancy in RCTreasury.sponsor(address,uint256) (contracts/RCTreasury.sol#466-482):
	External calls:
	- erc20.transferFrom(_sponsor,address(this),_amount) (contracts/RCTreasury.sol#478)
	State variables written after the call(s):
	- totalMarketPots += _amount (contracts/RCTreasury.sol#480)
Reentrancy in RCMarket.updateTimeHeldLimit(uint256,uint256) (contracts/RCMarket.sol#753-770):
	External calls:
	- _collectRent(_card) (contracts/RCMarket.sol#759)
		- treasury.payRent(_rentOwed) (contracts/RCMarket.sol#1060)
		- orderbook.reduceTimeHeldLimit(_user,_card,_timeHeldToIncrement) (contracts/RCMarket.sol#1066)
		- _timeUserForeclosed = treasury.collectRentUser(_user,block.timestamp) (contracts/RCMarket.sol#873-874)
		- treasury.refundUser(_user,_refundAmount) (contracts/RCMarket.sol#1020)
		- orderbook.findNewOwner(_card,_timeOfThisCollection) (contracts/RCMarket.sol#1025)
	- orderbook.setTimeHeldlimit(_user,_card,_timeHeldLimit) (contracts/RCMarket.sol#762)
	State variables written after the call(s):
	- cardTimeLimit[_card] = _timeHeldLimit (contracts/RCMarket.sol#765)
Reference: https://github.com/crytic/slither/wiki/Detector-Documentation#reentrancy-vulnerabilities-1

## Tools Used

Solidity Compiler 0.8.4
Hardhat v2.3.3
Slither v.0.8.0

Compiled, Tested, and Deployed contracts on a local Hardhat network.

Ran Slither-analyzer for further detecting and testing

## Recommended Mitigation Steps

(Worked best under a python virtual environment)
1. Clone project repository
3. Run project against hardhat network; 
    compile and run default test on contracts.
4. Installed sliither analyzer:
    https://github.com/crytic/slither
5. Ran [$ slither .] against all contracts
